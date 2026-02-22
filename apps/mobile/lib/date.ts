export function toKstDateString(d: Date) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export function formatKstLabel(dateKst: string) {
  // YYYY-MM-DD -> YYYY. MM. DD
  const [y, m, d] = dateKst.split('-');
  return `${y}. ${m}. ${d}`;
}

export function addDays(dateKst: string, deltaDays: number) {
  const [y, m, d] = dateKst.split('-').map((x) => parseInt(x, 10));
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + deltaDays);
  return toKstDateString(dt);
}

