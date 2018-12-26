export function cutName (s) {
  if (s.length < 6) return s
  return s.slice(0, 5) + '...'
}
