"""Component health evaluation and aggregation utilities."""

from collections.abc import Mapping, Sequence

STATUS_HEALTHY = 'HEALTHY'
STATUS_DEGRADED = 'DEGRADED'
STATUS_UNHEALTHY = 'UNHEALTHY'
VALID_STATUSES = frozenset({STATUS_HEALTHY, STATUS_DEGRADED, STATUS_UNHEALTHY})
DEFAULT_MAX_LATENCY_MS = 1000.0


def check_component_health(
    name: str,
    is_up: bool,
    latency_ms: float = 0.0,
    max_latency_ms: float = DEFAULT_MAX_LATENCY_MS,
) -> dict[str, object]:
  """Evaluates a component's health status against latency thresholds.

  Thresholds:
    - UNHEALTHY: `is_up` is False.
    - DEGRADED: `is_up` is True and `latency_ms > max_latency_ms`.
    - HEALTHY: `is_up` is True and `latency_ms <= max_latency_ms`.
  """
  stripped = name.strip()
  if not stripped:
    raise ValueError('Component name must not be empty.')
  if latency_ms < 0 or max_latency_ms < 0:
    raise ValueError('Latency values must be non-negative.')
  status = (
      STATUS_UNHEALTHY
      if not is_up
      else (STATUS_DEGRADED if latency_ms > max_latency_ms else STATUS_HEALTHY)
  )
  return {'name': stripped, 'status': status, 'latency_ms': float(latency_ms)}


def aggregate_health(components: Sequence[Mapping[str, object]]) -> str:
  """Returns worst-case health status across components."""
  worst = STATUS_HEALTHY
  for comp in components:
    status = comp.get('status')
    if status not in VALID_STATUSES:
      raise ValueError(f'Invalid status: {status!r}')
    if status == STATUS_UNHEALTHY:
      worst = STATUS_UNHEALTHY
    elif status == STATUS_DEGRADED and worst != STATUS_UNHEALTHY:
      worst = STATUS_DEGRADED
  return worst


def format_health_status(components: Sequence[Mapping[str, object]]) -> str:
  """Formats a single-line summary report of component health."""
  overall = aggregate_health(components)
  if not components:
    return f'Overall: {overall} (0/0 healthy)'
  healthy = sum(1 for c in components if c.get('status') == STATUS_HEALTHY)
  parts = []
  for comp in components:
    raw_name = comp.get('name')
    if not isinstance(raw_name, str) or not raw_name.strip():
      raise ValueError('Component name must be a non-empty string.')
    lat = float(comp.get('latency_ms', 0.0))  # type: ignore[arg-type]
    parts.append(f'{raw_name.strip()}={comp["status"]} ({lat:.1f}ms)')
  return (
      f'Overall: {overall} ({healthy}/{len(components)} healthy) | '
      f'{", ".join(parts)}'
  )
