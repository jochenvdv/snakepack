from pytest_harvest import is_main_process, get_xdist_worker_id, get_session_results_df


def pytest_sessionfinish(session):
    session_results_df = get_session_results_df(session)
    suffix = 'all' if is_main_process(session) else get_xdist_worker_id(session)
    session_results_df.to_csv('results_%s.csv' % suffix)