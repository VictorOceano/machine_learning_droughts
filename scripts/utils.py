import shutil
from pathlib import Path
import time
import json
import pandas as pd


def get_data_path() -> Path:
    # if the working directory is alread ml_drought don't need ../data
    if Path(".").absolute().as_posix().split("/")[-1] == "ml_drought":
        data_path = Path("data")
    elif Path(".").absolute().as_posix().split("/")[-3] == "ml_drought":
        data_path = Path("../../data")
    else:
        data_path = Path("../data")
    return data_path


def _rename_directory(
    from_path: Path, to_path: Path, with_datetime: bool = False
) -> None:
    if with_datetime:
        dt = time.gmtime()
        dt_str = f"{dt.tm_year}_{dt.tm_mon:02}_{dt.tm_mday:02}:{dt.tm_hour:02}{dt.tm_min:02}{dt.tm_sec:02}"
        name = "/" + dt_str + "_" + to_path.as_posix().split("/")[-1]
        to_path = "/".join(to_path.as_posix().split("/")[:-1]) + name
        to_path = Path(to_path)
    shutil.move(from_path.as_posix(), to_path.as_posix())
    print(f"MOVED {from_path} to {to_path}")


def get_results(dir_: Path, print: bool = True) -> pd.DataFrame:
    """ Display the results from the results.json """

    def _get_persistence_for_group(x):
        return x.loc[x.model == 'previous_month'].total_rmse

    # create a dataframe for the results in results.json
    result_paths = [p for p in dir_.glob('*/*/results.json')]
    experiments = [
        re.sub(date_regex, '', p.parents[1].name)
        for p in result_paths
    ]
    df = pd.DataFrame({'experiment': experiments})

    # match the date_str if in the experiment name
    date_regex = r'\d{4}_\d{2}_\d{2}:\d{6}_'
    df['time'] = [
        re.match(date_regex, p.parents[1].name)
        for p in result_paths
    ]
    df['model'] = [p.parents[0].name for p in result_paths]
    result_dicts = [json.load(open(p, 'rb')) for p in result_paths]
    df['total_rmse'] = [d['total'] for d in result_dicts]

    persistence_rmses = df.groupby(
        'experiment'
    ).apply(_get_persistence_for_group).reset_index()

    if print:
        for i, row in df.iterrows():
            persistence_score = persistence_rmses[
                'total_rmse'
            ].loc[persistence_rmses.experiment == row.experiment].values

            print(
                f"Experiment: {row.experiment}\n"
                f"Model: {row.model}\n"
                f"Persistence RMSE: {persistence_score}\n"
                f"RMSE: {row.total_rmse}\n"
            )

    return df

