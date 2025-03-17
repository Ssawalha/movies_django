from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
from pprint import pprint

def get_current_year():
    return datetime.now().strftime('%Y')

def get_current_month():
    return datetime.now().strftime('%m')

def normalize_title(title):
    return title.lower().strip()

def handle_raw_titles(titles):
    titles_df = pd.DataFrame(titles)
    if not(titles_df.empty):
        if not(is_merged_df(titles_df)):
            titles_df['normalized_title'] = titles_df.get('title').apply(normalize_title)
    return titles_df

def format_merged_titles(titles_df):
    titles = []
    for _, row in titles_df.iterrows():
        titles.append({
            'title_grand': row.get('title_grand', row.get('title') if row.get('grand_id') else ''),
            'grand_id': row.get('grand_id', ''),
            'normalized_title': row.get('normalized_title', ''),
            'title_prime': row.get('title_prime', row.get('title') if row.get('prime_id') else ''),
            'prime_id': row.get('prime_id', ''),
            'title_taj': row.get('title_taj',  row.get('title') if row.get('taj_id') else ''),
            'taj_id': row.get('taj_id', ''),
            'title': '',
        })
    return titles

def get_suffix(titles_df):
    if titles_df.empty:
        raise ValueError('Empty dataframe') 
    if not is_merged_df(titles_df):
        return 'taj' if 'taj_id' in titles_df.columns else ('grand' if 'grand_id' in titles_df.columns else 'prime')
    return 'merged'

def is_merged_df(titles_df):
    source_columns = ['grand_id', 'prime_id', 'taj_id']
    source_count = sum(1 for col in source_columns if col in titles_df.columns)
    return source_count > 1

def handle_perfect_match_titles(*args):
    raw_dfs = [handle_raw_titles(titles) for titles in args if titles]

    if not raw_dfs:
        raise ValueError('No titles to match')

    merged_df = raw_dfs[0]
    for df in raw_dfs[1:]:
        suffix = get_suffix(df)
        merged_df = pd.merge(merged_df, df, on='normalized_title', how='outer', suffixes=('', f'_{suffix}'))

    merged_df = merged_df.fillna('')
    print("Perfect Match DataFrame:\n", merged_df)
    return format_merged_titles(merged_df)

def should_merge_fuzzy_match_titles(title_a, title_b):
    if (title_a['prime_id'] and title_b['prime_id']) or \
    (title_a['grand_id'] and title_b['grand_id']) or \
    (title_a['taj_id'] and title_b['taj_id']):
        print(f"Not merging: {title_a} and {title_b}")
        return False
    print(f"Should merge: {title_a} and {title_b}")

    return True

def get_first_non_empty(*values):
    return next((v for v in values if v), '')

def merge_fuzzy_match_titles(title_a, title_b):
    id_count_a = sum(1 for key in ['grand_id', 'prime_id', 'taj_id'] if title_a.get(key))
    id_count_b = sum(1 for key in ['grand_id', 'prime_id', 'taj_id'] if title_b.get(key))

    if id_count_a > id_count_b:
        title, normalized_title = title_a['title'], title_a['normalized_title']
    elif id_count_b > id_count_a:
        title, normalized_title = title_b['title'], title_b['normalized_title']
    else: # prioritize prime
        if title_a.get('title_prime') != '':
            title, normalized_title = title_a['title'], title_a['normalized_title']
        else:
            title, normalized_title = title_b['title'], title_b['normalized_title']

    merged = {
        'title_grand': get_first_non_empty(title_a.get('title_grand'), title_b.get('title_grand')),
        'grand_id': get_first_non_empty(title_a.get('grand_id'), title_b.get('grand_id')),
        'normalized_title': normalized_title,
        'title_prime': get_first_non_empty(title_a.get('title_prime'), title_b.get('title_prime')),
        'prime_id': get_first_non_empty(title_a.get('prime_id'), title_b.get('prime_id')),
        'title_taj': get_first_non_empty(title_a.get('title_taj'), title_b.get('title_taj')),
        'taj_id': get_first_non_empty(title_a.get('taj_id'), title_b.get('taj_id')),
        'title': title
    }
    print(f"merge_fuzzy_match_titles: {merged}")
    return merged

def fuzzy_match_titles(titles):
    titles_df = pd.DataFrame(titles)
    titles_df['fuzzy_match'] = None

    for i, row in titles_df.iterrows():
        title = row['normalized_title']
        # Exclude the current row from the list of potential matches
        potential_matches = titles_df[titles_df.index != i]['normalized_title'].tolist()
        best_match = process.extractOne(title, potential_matches, scorer=fuzz.ratio)
        if best_match and best_match[1] > 70:
            titles_df.at[i, 'fuzzy_match'] = best_match[0]

    return titles_df

def handle_fuzzy_match_titles(titles):
    # TODO refactor. Wrong and spaghetti.
    handled_titles = []
    titles_df = fuzzy_match_titles(titles)
    for i, row in titles_df.iterrows():
        for j, row2 in titles_df.iterrows():
            if i != j:
                if row['normalized_title'] == row2['fuzzy_match'] and should_merge_fuzzy_match_titles(row, row2):
                    merged = merge_fuzzy_match_titles(row.to_dict(), row2.to_dict())
                    handled_titles.append(merged)

                    # Remove the merged titles from the list
                    titles_df = titles_df.drop([titles_df.index[i], j])
                    break # back to main loop. We need to recheck the current row with the new list
    
    # Add the remaining titles that didn't match
    titles_df = titles_df.drop('fuzzy_match', axis=1)
    for i, row in titles_df.iterrows():
        handled_titles.append(row.to_dict())
    print("Fuzzy Merged Titles:\n", handled_titles)
    return handled_titles

def match_titles(grand_titles, prime_titles, taj_titles):
    matched_titles = handle_perfect_match_titles(grand_titles, prime_titles, taj_titles)
    matched_titles = handle_fuzzy_match_titles(matched_titles)
    print("FINALLY MATCHED TITLES:\n")
    pprint(matched_titles)
    return matched_titles

