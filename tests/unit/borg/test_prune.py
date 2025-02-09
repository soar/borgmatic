import logging
from collections import OrderedDict

from flexmock import flexmock

from borgmatic.borg import prune as module

from ..test_verbosity import insert_logging_mock


def insert_execute_command_mock(prune_command, **kwargs):
    flexmock(module).should_receive('execute_command').with_args(prune_command).once()


BASE_PRUNE_FLAGS = (('--keep-daily', '1'), ('--keep-weekly', '2'), ('--keep-monthly', '3'))


def test_make_prune_flags_returns_flags_from_config_plus_default_prefix():
    retention_config = OrderedDict((('keep_daily', 1), ('keep_weekly', 2), ('keep_monthly', 3)))

    result = module._make_prune_flags(retention_config)

    assert tuple(result) == BASE_PRUNE_FLAGS + (('--prefix', '{hostname}-'),)


def test_make_prune_flags_accepts_prefix_with_placeholders():
    retention_config = OrderedDict((('keep_daily', 1), ('prefix', 'Documents_{hostname}-{now}')))

    result = module._make_prune_flags(retention_config)

    expected = (('--keep-daily', '1'), ('--prefix', 'Documents_{hostname}-{now}'))

    assert tuple(result) == expected


def test_make_prune_flags_treats_empty_prefix_as_no_prefix():
    retention_config = OrderedDict((('keep_daily', 1), ('prefix', '')))

    result = module._make_prune_flags(retention_config)

    expected = (('--keep-daily', '1'),)

    assert tuple(result) == expected


def test_make_prune_flags_treats_none_prefix_as_no_prefix():
    retention_config = OrderedDict((('keep_daily', 1), ('prefix', None)))

    result = module._make_prune_flags(retention_config)

    expected = (('--keep-daily', '1'),)

    assert tuple(result) == expected


PRUNE_COMMAND = (
    'borg',
    'prune',
    'repo',
    '--keep-daily',
    '1',
    '--keep-weekly',
    '2',
    '--keep-monthly',
    '3',
)


def test_prune_archives_calls_borg_with_parameters():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND)

    module.prune_archives(
        dry_run=False, repository='repo', storage_config={}, retention_config=retention_config
    )


def test_prune_archives_with_log_info_calls_borg_with_info_parameter():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--stats', '--info'))
    insert_logging_mock(logging.INFO)

    module.prune_archives(
        repository='repo', storage_config={}, dry_run=False, retention_config=retention_config
    )


def test_prune_archives_with_log_debug_calls_borg_with_debug_parameter():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--stats', '--debug', '--list', '--show-rc'))
    insert_logging_mock(logging.DEBUG)

    module.prune_archives(
        repository='repo', storage_config={}, dry_run=False, retention_config=retention_config
    )


def test_prune_archives_with_dry_run_calls_borg_with_dry_run_parameter():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--dry-run',))

    module.prune_archives(
        repository='repo', storage_config={}, dry_run=True, retention_config=retention_config
    )


def test_prune_archives_with_local_path_calls_borg_via_local_path():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(('borg1',) + PRUNE_COMMAND[1:])

    module.prune_archives(
        dry_run=False,
        repository='repo',
        storage_config={},
        retention_config=retention_config,
        local_path='borg1',
    )


def test_prune_archives_with_remote_path_calls_borg_with_remote_path_parameters():
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--remote-path', 'borg1'))

    module.prune_archives(
        dry_run=False,
        repository='repo',
        storage_config={},
        retention_config=retention_config,
        remote_path='borg1',
    )


def test_prune_archives_with_umask_calls_borg_with_umask_parameters():
    storage_config = {'umask': '077'}
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--umask', '077'))

    module.prune_archives(
        dry_run=False,
        repository='repo',
        storage_config=storage_config,
        retention_config=retention_config,
    )


def test_prune_archives_with_lock_wait_calls_borg_with_lock_wait_parameters():
    storage_config = {'lock_wait': 5}
    retention_config = flexmock()
    flexmock(module).should_receive('_make_prune_flags').with_args(retention_config).and_return(
        BASE_PRUNE_FLAGS
    )
    insert_execute_command_mock(PRUNE_COMMAND + ('--lock-wait', '5'))

    module.prune_archives(
        dry_run=False,
        repository='repo',
        storage_config=storage_config,
        retention_config=retention_config,
    )
