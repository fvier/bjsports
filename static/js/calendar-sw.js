self.addEventListener('push', event => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch (_) {
    payload = {body: event.data?.text() || 'Você tem uma aula chegando.'};
  }
  event.waitUntil(self.registration.showNotification(payload.title || 'BJ Sports', {
    body: payload.body || 'Você tem uma aula chegando.',
    icon: payload.icon || '/static/img/favicon.png',
    badge: '/static/img/favicon.png',
    tag: payload.tag || 'bjsports-calendar-reminder',
    data: {url: payload.url || '/calendario'}
  }));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || '/calendario';
  event.waitUntil(clients.matchAll({type: 'window', includeUncontrolled: true}).then(windows => {
    const existing = windows.find(client => new URL(client.url).pathname === targetUrl);
    return existing ? existing.focus() : clients.openWindow(targetUrl);
  }));
});
