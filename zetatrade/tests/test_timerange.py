# pragma pylint: disable=missing-docstring, C0103
import pytest

from earthzetaorg.configuration import TimeRange


def test_parse_timerange_incorrect() -> None:
    assert TimeRange(None, 'line', 0, -200) == TimeRange.parse_timerange('-200')
    assert TimeRange('line', None, 200, 0) == TimeRange.parse_timerange('200-')
    assert TimeRange('index', 'index', 200, 500) == TimeRange.parse_timerange('200-500')

    assert TimeRange('date', None, 1274486400, 0) == TimeRange.parse_timerange('20100522-')
    assert TimeRange(None, 'date', 0, 1274486400) == TimeRange.parse_timerange('-20100522')
    timerange = TimeRange.parse_timerange('20100522-20150730')
    assert timerange == TimeRange('date', 'date', 1274486400, 1438214400)

    # Added test for unix timestamp - BTC genesis date
    assert TimeRange('date', None, 1231006505, 0) == TimeRange.parse_timerange('1231006505-')
    assert TimeRange(None, 'date', 0, 1233360000) == TimeRange.parse_timerange('-1233360000')
    timerange = TimeRange.parse_timerange('1231006505-1233360000')
    assert TimeRange('date', 'date', 1231006505, 1233360000) == timerange

    # TODO: Find solution for the following case (passing timestamp in ms)
    timerange = TimeRange.parse_timerange('1231006505000-1233360000000')
    assert TimeRange('date', 'date', 1231006505, 1233360000) != timerange

    with pytest.raises(Exception, match=r'Incorrect syntax.*'):
        TimeRange.parse_timerange('-')
