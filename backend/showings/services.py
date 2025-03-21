import logging

import pandas as pd
from fuzzywuzzy import fuzz, process
from showings.clients import GrandClient, PrimeClient, TajClient
from showings.parsers import GrandParser, PrimeParser, TajParser
from showings.util import get_first_non_empty

logger = logging.getLogger(__name__)
# TODO SERIALIZERS!


class GrandService:
    client = GrandClient
    parser = GrandParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = GrandService.get_titles()
            for title in titles:
                showing_dates = GrandService.get_showing_dates(title)
                for date in showing_dates:
                    showing_times = GrandService.get_showing_times(title, date)
                    for time in showing_times:
                        showings.append(
                            {
                                "title": title.get("title"),
                                "date": date,
                                "time": time,
                                "location": "Grand Cinema City Mall",  # TODO make constant?
                            }
                        )
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_titles() -> list:
        try:
            titles_page = GrandService.client.get_titles_page()
            titles = GrandService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_showing_dates(title):
        title_id = title.get("grand_id")
        try:
            showing_dates_page = GrandService.client.get_title_showing_dates(title_id)
            showing_dates = GrandService.parser.parse_showing_dates(showing_dates_page)
            return showing_dates
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_showing_times(title, date):
        title_id = title.get("grand_id")
        try:
            showing_times_page = GrandService.client.get_title_showing_times_on_date(
                title_id, date
            )
            showing_times = GrandService.parser.parse_showing_times(showing_times_page)
            return showing_times
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise GrandService.GrandServiceError(f"An error occurred: {e}")

    class GrandServiceError(Exception):
        pass


class TajService:
    client = TajClient
    parser = TajParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = TajService.get_titles()
            for t in titles:
                showings += TajService.get_title_showings(t)
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_titles() -> list:
        try:
            titles_page = TajService.client.get_titles_page()
            titles = TajService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showings(title) -> list:
        title_showings = []
        try:
            title_page = TajService.client.get_title_showings_page(title)
            parsed_dates = TajService.parser.parse_showing_dates_from_title_page(
                title_page
            )
            parsed_times = TajService.parser.parse_showing_times_from_title_page(
                title_page, parsed_dates
            )
            for t in parsed_times:
                t["title"] = title["title"]
                t["location"] = "Taj Mall"  # TODO make constant?
                del t["date_id"]
                title_showings.append(t)
            return title_showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise TajService.TajServiceError(f"An error occurred: {e}")

    class TajServiceError(Exception):
        pass


class PrimeService:
    client = PrimeClient
    parser = PrimeParser

    @staticmethod
    def get_showings() -> list:
        showings = []
        try:
            titles = PrimeService.get_titles()
            for title in titles:
                showings += PrimeService.get_title_showings(title)
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_titles() -> list:
        try:
            titles_page = PrimeService.client.get_titles_page()
            titles = PrimeService.parser.parse_titles_from_titles_page(titles_page)
            return titles
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")

    @staticmethod
    def get_title_showings(title: dict) -> list:
        try:
            title_showings_page = PrimeService.client.get_title_showings_page(title)
            showings = PrimeService.parser.parse_showings_from_title_page(
                title_showings_page
            )
            showings = [
                {
                    "title": title["prime_id"],
                    "date": s["date"],
                    "time": s["time"],
                    "location": s["location"],
                }
                for s in showings
            ]
            return showings
        except Exception as e:
            logger.error(f"{__class__.__name__} An error occurred: {e}")
            raise PrimeService.PrimeServiceError(f"An error occurred: {e}")

    class PrimeServiceError(Exception):
        pass


class TitleMatchService:
    @staticmethod
    def normalize_title(title):
        return title.lower().strip()

    @staticmethod
    def match_titles(grand_titles, prime_titles, taj_titles):
        matched_titles = TitleMatchService.handle_perfect_match_titles(
            grand_titles, prime_titles, taj_titles
        )
        matched_titles = TitleMatchService.handle_fuzzy_match_titles(matched_titles)
        return matched_titles

    @staticmethod
    def handle_fuzzy_match_titles(titles):
        # TODO refactor. Wrong and spaghetti.
        handled_titles = []
        processed_indices = set()
        titles_df = TitleMatchService.fuzzy_match_titles(titles)

        # Add column with number of matches and sort
        titles_df["match_count"] = titles_df["fuzzy_matches"].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        titles_df = titles_df.sort_values("match_count", ascending=False)

        # Iterate through rows in order of most matches
        for idx, row in titles_df.iterrows():
            if idx in processed_indices:
                continue

            processed_indices.add(idx)
            current_merged = row.to_dict()

            # If row has matches, merge with each match
            if isinstance(row["fuzzy_matches"], list):
                for match_idx in row["fuzzy_matches"]:
                    if match_idx not in processed_indices:
                        match_row = titles_df.loc[match_idx]
                        if TitleMatchService.should_merge_fuzzy_match_titles(
                            current_merged, match_row
                        ):
                            current_merged = TitleMatchService.merge_fuzzy_match_titles(
                                current_merged, match_row.to_dict()
                            )
                            processed_indices.add(match_idx)

            # Clean up extra fields before adding to results
            if "fuzzy_matches" in current_merged:
                del current_merged["fuzzy_matches"]
            if "match_count" in current_merged:
                del current_merged["match_count"]

            handled_titles.append(current_merged)
        return handled_titles

    @staticmethod
    def fuzzy_match_titles(titles):
        titles_df = pd.DataFrame(titles)
        titles_df["fuzzy_matches"] = None

        for i, row in titles_df.iterrows():
            title = row["normalized_title"]
            # Exclude the current row from the list of potential matches
            other_rows = titles_df[titles_df.index != i]
            # Get all matches above threshold (70)
            matches = process.extract(
                title,
                other_rows["normalized_title"].tolist(),
                scorer=fuzz.ratio,
                limit=None,
            )
            # Filter matches above threshold and get indices of matching rows
            good_matches = [
                other_rows.index[other_rows["normalized_title"] == match[0]].item()
                for match in matches
                if match[1] > 70
            ]

            if good_matches:
                titles_df.at[i, "fuzzy_matches"] = good_matches

        return titles_df

    @staticmethod
    def merge_fuzzy_match_titles(title_a, title_b):
        id_count_a = sum(
            1 for key in ["grand_id", "prime_id", "taj_id"] if title_a.get(key)
        )
        id_count_b = sum(
            1 for key in ["grand_id", "prime_id", "taj_id"] if title_b.get(key)
        )

        if id_count_a > id_count_b:
            title, normalized_title = title_a["title"], title_a["normalized_title"]
        elif id_count_b > id_count_a:
            title, normalized_title = title_b["title"], title_b["normalized_title"]
        else:  # prioritize prime
            if title_a.get("title_prime") != "":
                title, normalized_title = title_a["title"], title_a["normalized_title"]
            else:
                title, normalized_title = title_b["title"], title_b["normalized_title"]

        merged = {
            "title_grand": get_first_non_empty(
                title_a.get("title_grand"), title_b.get("title_grand")
            ),
            "grand_id": get_first_non_empty(
                title_a.get("grand_id"), title_b.get("grand_id")
            ),
            "normalized_title": normalized_title,
            "title_prime": get_first_non_empty(
                title_a.get("title_prime"), title_b.get("title_prime")
            ),
            "prime_id": get_first_non_empty(
                title_a.get("prime_id"), title_b.get("prime_id")
            ),
            "title_taj": get_first_non_empty(
                title_a.get("title_taj"), title_b.get("title_taj")
            ),
            "taj_id": get_first_non_empty(title_a.get("taj_id"), title_b.get("taj_id")),
            "title": title,
        }
        return merged

    @staticmethod
    def handle_raw_titles(titles):
        titles_df = pd.DataFrame(titles)
        if not (titles_df.empty):
            if not (TitleMatchService.is_merged_df(titles_df)):
                titles_df["normalized_title"] = titles_df.get("title").apply(
                    TitleMatchService.normalize_title
                )
        return titles_df

    @staticmethod
    def format_merged_titles(titles_df):
        titles = []
        for _, row in titles_df.iterrows():
            titles.append(
                {
                    "title_grand": row.get(
                        "title_grand", row.get("title") if row.get("grand_id") else ""
                    ),
                    "grand_id": row.get("grand_id", ""),
                    "normalized_title": row.get("normalized_title", ""),
                    "title_prime": row.get(
                        "title_prime", row.get("title") if row.get("prime_id") else ""
                    ),
                    "prime_id": row.get("prime_id", ""),
                    "title_taj": row.get(
                        "title_taj", row.get("title") if row.get("taj_id") else ""
                    ),
                    "taj_id": row.get("taj_id", ""),
                    "title": "",
                }
            )
        return titles

    @staticmethod
    def get_suffix(titles_df):
        if titles_df.empty:
            raise ValueError("Empty dataframe")
        if not TitleMatchService.is_merged_df(titles_df):
            return (
                "taj"
                if "taj_id" in titles_df.columns
                else ("grand" if "grand_id" in titles_df.columns else "prime")
            )
        return "merged"

    @staticmethod
    def is_merged_df(titles_df):
        source_columns = ["grand_id", "prime_id", "taj_id"]
        source_count = sum(1 for col in source_columns if col in titles_df.columns)
        return source_count > 1

    @staticmethod
    def handle_perfect_match_titles(*args):
        raw_dfs = [
            TitleMatchService.handle_raw_titles(titles) for titles in args if titles
        ]

        if not raw_dfs:
            raise ValueError("No titles to match")

        merged_df = raw_dfs[0]
        for df in raw_dfs[1:]:
            suffix = TitleMatchService.get_suffix(df)
            merged_df = pd.merge(
                merged_df,
                df,
                on="normalized_title",
                how="outer",
                suffixes=("", f"_{suffix}"),
            )

        merged_df = merged_df.fillna("")
        return TitleMatchService.format_merged_titles(merged_df)

    @staticmethod
    def should_merge_fuzzy_match_titles(title_a, title_b):
        if (
            (title_a["prime_id"] and title_b["prime_id"])
            or (title_a["grand_id"] and title_b["grand_id"])
            or (title_a["taj_id"] and title_b["taj_id"])
        ):
            return False
        return True
