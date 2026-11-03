"""Unit tests for health_util."""

import unittest
import health_util as hu


class HealthUtilTest(unittest.TestCase):
  """Tests for health_util functions."""

  def test_check_component_health(self) -> None:
    fn = hu.check_component_health
    self.assertEqual(
        fn(' db ', True, 50.0, 100.0),
        {'name': 'db', 'status': 'HEALTHY', 'latency_ms': 50.0},
    )
    self.assertEqual(fn('db', True, 100.0, 100.0)['status'], hu.STATUS_HEALTHY)
    self.assertEqual(
        fn('db', True, 0.0, 0.0)['status'], hu.STATUS_HEALTHY
    )
    self.assertEqual(
        fn('db', True, 0.1, 0.0)['status'], hu.STATUS_DEGRADED
    )
    self.assertEqual(
        fn('db', True, hu.DEFAULT_MAX_LATENCY_MS)['status'], hu.STATUS_HEALTHY
    )
    self.assertEqual(
        fn('db', True, 100.1, 100.0)['status'], hu.STATUS_DEGRADED
    )
    self.assertEqual(
        fn('db', False, 10.0, 100.0)['status'], hu.STATUS_UNHEALTHY
    )
    for bad in ('', '   '):
      with self.assertRaises(ValueError):
        fn(bad, True)
    for kw in ({'latency_ms': -1.0}, {'max_latency_ms': -0.1}):
      with self.assertRaises(ValueError):
        fn('db', True, **kw)

  def test_aggregate_health(self) -> None:
    agg, fn = hu.aggregate_health, hu.check_component_health
    self.assertEqual(agg([]), 'HEALTHY')
    c_ok = fn('a', True, 10.0)
    c_deg = fn('b', True, 2000.0)
    c_down = fn('c', False)
    self.assertEqual(agg([c_ok]), 'HEALTHY')
    self.assertEqual(agg([c_ok, c_deg]), 'DEGRADED')
    self.assertEqual(agg([c_deg, c_down, c_ok]), 'UNHEALTHY')
    for bad in ({}, {'status': 'UNKNOWN'}):
      with self.assertRaises(ValueError):
        agg([bad])

  def test_format_health_status(self) -> None:
    fmt, fn = hu.format_health_status, hu.check_component_health
    self.assertEqual(fmt([]), 'Overall: HEALTHY (0/0 healthy)')
    comps = [fn('api', True, 12.34), fn('cache', True, 1500.0)]
    self.assertEqual(
        fmt(comps),
        'Overall: DEGRADED (1/2 healthy) | '
        'api=HEALTHY (12.3ms), cache=DEGRADED (1500.0ms)',
    )
    for bad in ({'status': 'HEALTHY'}, {'name': '  ', 'status': 'HEALTHY'}):
      with self.assertRaises(ValueError):
        fmt([bad])


if __name__ == '__main__':
  unittest.main()
