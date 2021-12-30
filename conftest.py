from pathlib import Path

from pytest_harvest import is_main_process, get_xdist_worker_id, get_session_results_df


def pytest_sessionfinish(session):
    session_results_df = get_session_results_df(session)
    suffix = 'all' if is_main_process(session) else get_xdist_worker_id(session)
    session_results_df = _clean_result_data(session_results_df)
    session_results_df.to_csv('results_%s.csv' % suffix)


def _clean_result_data(df):
    return df.drop(columns=['pytest_obj'])
