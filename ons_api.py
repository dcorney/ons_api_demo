# Simple demo of how to access data from the ONS API
import requests
import pandas as pd
import pprint as pp
import logging

logger = logging.getLogger(__name__)

ROOT_URL = "https://api.beta.ons.gov.uk/v1/"


def get_list_of_datasets():
    """Get list of all datasets available from API.
    Currently (August 2021), there are 41 available datasets.

    Returns
    -------
    list of dicts
        Metadata objects for each available dataset.
    """
    num_to_get = 100
    datasets = []

    offset = 0
    while len(datasets) < num_to_get:
        r = requests.get(ROOT_URL + "datasets", params={"offset": offset})
        results = r.json()
        [logger.info(item.get("title")) for item in results.get("items")]
        datasets.extend(results.get("items"))
        num_retrieved = results.get("count")
        offset += num_retrieved
        if num_retrieved == 0:
            break
    logger.info(f"\nFound {len(datasets)} datasets")
    return datasets


def get_dataset_by_name(datasets, target_name):
    """Get a dataset by matching on its title (or part of the title).
    Returns the first dataset object whose name contains the given target_name string.

    Parameters
    ----------
    datasets : List
        List of dataset objects
    target_name : str
        name (or partial name) of target dataset

    Returns
    -------
    dict
        Dataset object (or None, if no match is found)
    """
    for ds in datasets:
        if target_name.lower() in ds.get("title").lower():
            logger.info(f"Found dataset '{ds.get('title')}'")
            return ds
    logger.info(f"No dataset found containing '{target_name}'")
    return None


def get_edition(dataset, prefered_edition="time-series"):
    """Get one edition of a dataset. If no preferred edition is
    specified, return the most recent one.

    Parameters
    ----------
    dataset : dict
        dataset metadata
    prefered_edition : str, optional
        name of edition, by default "time-series"

    Returns
    -------
    str
        URL of edition
    """
    editions_url = dataset.get("links").get("editions").get("href")
    r = requests.get(editions_url)
    results = r.json()
    for row in results.get("items"):
        if row.get("edition") == prefered_edition:
            edition = row.get("links").get("latest_version").get("href")
            return edition

    # Default to latest version, if requested version is not found.
    latest_version = dataset.get("links").get("latest_version").get("href")
    return latest_version


def get_dimensions(edition_url):
    """Builds dictionary of all valid options for all dimensions of a given dataset,
    with descriptions for each option.
    Individual obvserviations can later be obtained by choosing from these options.
    Ranges can later be obtained by replacing one dimesion with the wildcard '*'.

    Parameters
    ----------
    dataset : dict
        single dataset

    Returns
    -------
    dict of dicts
        map of {dimensions:{acceptable_values:description}}
    """
    valid_dimensions = {}
    r = requests.get(edition_url + "/dimensions")
    results = r.json()
    for dimension in results.get("items"):
        logger.info(f'{dimension.get("name")}: \t{dimension.get("label")}')
        dim_id = dimension.get("links").get("options").get("id")
        options_url = f"{edition_url}/dimensions/{dim_id}/options"

        sr = requests.get(options_url, params={"limit": 50})
        sresults = sr.json()
        # TODO! Could add in paging here, as there *could* be multiple pages of valid options.
        logger.info(f"\tHas {sresults.get('count')} options")
        # valid_options = [item.get("option") for item in sresults.get("items")]
        option_descriptions = {
            item.get("option"): item.get("label") for item in sresults.get("items")
        }
        logger.info(f'{dimension.get("name")}: {option_descriptions}')
        valid_dimensions[dimension.get("name")] = option_descriptions

    return valid_dimensions


def choose_dimensions(valid_dims, overrides={}):
    """For each dimension, choose a single valid option (except for 'time', where
    we use the wildcard '*' to get the whole time-series.)
    If not specified, choose the first valid option for each dimension.

    Parameters
    ----------
    valid_dims : dict
        map of lists of valid dimension values
    overrides : dict, optional
        selected dimensions

    Returns
    -------
    dict
        final choice of dimensions
    """
    # By default, choose first valid item for all dimensions; then override where needed:
    chosen_dimensions = {k: next(iter(v.keys())) for k, v in valid_dims.items()}
    # get whole time-series, not just a single point in time:
    chosen_dimensions["time"] = "*"
    chosen_dimensions.update(overrides)
    return chosen_dimensions


def get_observations(edition_url, dimensions):
    """[summary]

    Parameters
    ----------
    edition_url : str
        URL of this edition of the data
    dimensions : dict
        dimensions specifying slice of data required

    Returns
    -------
    pd.Dataframe
        Summary of data, with columns "id" (time) and "observation" (value)
    """
    r = requests.get(edition_url + "/observations", params=dimensions)
    results = r.json()
    summary = []
    for observation in results.get("observations"):
        id = observation.get("dimensions").get("Time").get("id")
        summary.append({"id": id, "observation": observation.get("observation")})
    df = pd.DataFrame(summary)
    return df


def get_timeseries(dataset_name, dimension_values):
    """Get a specified dataset time-series, with a given set of dimensions.
    NB: dataframe is not sorted.

    Parameters
    ----------
    dataset_name : str
        Descriptive name of data set.
    dimension_values : dict
        set of valid dimensions for this dataset.
        If set to "None", then return set of valid dimesions.

    Returns
    -------
    Either:
        dict
            Set of valid dimensions, if None specified in function call
    or:
        dataframe
            containing time series
        dict
            dataset metadata
        str
            url of this edition of the data
    """
    dss = get_list_of_datasets()
    ds = get_dataset_by_name(dss, dataset_name)
    edition_url = get_edition(ds)
    valid_dims = get_dimensions(edition_url)
    logger.info(valid_dims)
    if dimension_values is None:
        return valid_dims
    chosen_dimensions = choose_dimensions(valid_dims, dimension_values)
    df = get_observations(edition_url, chosen_dimensions)
    logger.info(df.shape)
    return df, ds, edition_url


def demo():
    print("=" * 70)
    print("List of available datasets:")
    dss = get_list_of_datasets()
    [print(item.get("title")) for item in dss]

    print("=" * 70)
    dataset_name = "UK Labour Market"
    print(f"Valid options for dimensions for the {dataset_name}, with descriptions")
    # Get the set of valid dimensions for the Labour Market set.
    # E.g. list of valid age groups, economic activity categories etc.

    dimensions = get_timeseries(dataset_name, None)
    pp.pprint(dimensions)
    print("\n")

    # We've now selected specific dimensions for our request:
    labour_market_dimensions = {
        "economicactivity": "in-employment",
        "agegroups": "16+",
        "seasonaladjustment": "seasonal-adjustment",
        "sex": "all-adults",
        "unitofmeasure": "rates",
    }
    print(f"Chosen dimensions for the {dataset_name}")
    pp.pprint(labour_market_dimensions, indent=4)

    df_labour = get_timeseries(dataset_name, labour_market_dimensions)[0]
    df_labour["year"] = (
        df_labour["id"].str[-4:].astype(int)
    )  # extract year as last 4 digits of row id
    df_labour = df_labour.sort_values("year")
    print("")
    print(df_labour)
    print("\n")

    # Repeat the process for a second time series, GDP, with specific dimensions:
    print("=" * 70)
    gdp_dataset_name = "annual GDP"
    gdp_dimensions = {
        "geography": "UK0",
        "unofficialstandardindustrialclassification": "A--T",
    }
    print(f"Chosen dimensions for the {dataset_name}")
    df_gdp = get_timeseries(gdp_dataset_name, gdp_dimensions)[0]
    df_gdp = df_gdp.sort_values("id")
    pp.pprint(gdp_dimensions, indent=4)
    print("")
    print(gdp_dataset_name)
    print(df_gdp)

    print("=" * 70)
    print("End of demo!")


if __name__ == "__main__":
    demo()
