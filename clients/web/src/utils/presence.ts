export const presenceBadge = (presence: string): 'success' | 'warning' | 'error' | 'default' => {
  switch (presence) {
    case 'online':         return 'success'
    case 'away':           return 'warning'
    case 'do_not_disturb': return 'error'
    default:               return 'default'
  }
}
