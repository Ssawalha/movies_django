from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd

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
    return format_merged_titles(merged_df)

def should_merge_fuzzy_match_titles(title_a, title_b):
    if (title_a['prime_id'] and title_b['prime_id']) or \
    (title_a['grand_id'] and title_b['grand_id']) or \
    (title_a['taj_id'] and title_b['taj_id']):
        return False
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
    return merged

def fuzzy_match_titles(titles):
    titles_df = pd.DataFrame(titles)
    titles_df['fuzzy_matches'] = None

    for i, row in titles_df.iterrows():
        title = row['normalized_title']
        # Exclude the current row from the list of potential matches
        other_rows = titles_df[titles_df.index != i]
        # Get all matches above threshold (70)
        matches = process.extract(title, other_rows['normalized_title'].tolist(), scorer=fuzz.ratio, limit=None)
        # Filter matches above threshold and get indices of matching rows
        good_matches = [other_rows.index[other_rows['normalized_title'] == match[0]].item() 
                       for match in matches if match[1] > 70]
        
        if good_matches:
            titles_df.at[i, 'fuzzy_matches'] = good_matches

    return titles_df

def handle_fuzzy_match_titles(titles):
    # TODO refactor. Wrong and spaghetti.
    handled_titles = []
    processed_indices = set()
    titles_df = fuzzy_match_titles(titles)
    
    # Add column with number of matches and sort
    titles_df['match_count'] = titles_df['fuzzy_matches'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    titles_df = titles_df.sort_values('match_count', ascending=False)

    # Iterate through rows in order of most matches
    for idx, row in titles_df.iterrows():
        if idx in processed_indices:
            continue
            
        processed_indices.add(idx)
        current_merged = row.to_dict()
        
        # If row has matches, merge with each match
        if isinstance(row['fuzzy_matches'], list):
            for match_idx in row['fuzzy_matches']:
                if match_idx not in processed_indices:
                    match_row = titles_df.loc[match_idx]
                    if should_merge_fuzzy_match_titles(current_merged, match_row):
                        current_merged = merge_fuzzy_match_titles(current_merged, match_row.to_dict())
                        processed_indices.add(match_idx)
        
        # Clean up extra fields before adding to results
        if 'fuzzy_matches' in current_merged:
            del current_merged['fuzzy_matches']
        if 'match_count' in current_merged:
            del current_merged['match_count']
            
        handled_titles.append(current_merged)    
    return handled_titles

def match_titles(grand_titles, prime_titles, taj_titles):
    matched_titles = handle_perfect_match_titles(grand_titles, prime_titles, taj_titles)
    matched_titles = handle_fuzzy_match_titles(matched_titles)
    return matched_titles

