import React, { useEffect, useState } from 'react';

interface EventsPageProps {
  token: string;
}

interface Event {
  id: string;
  name: string;
  timestamp: string;
}

const API_URL = import.meta.env.VITE_API_URL || '';

const EventsPage: React.FC<EventsPageProps> = ({ token }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch(`${API_URL}/api/events`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to fetch events');
        const data = await res.json();
        setEvents(data.events || []);
      } catch (err) {
        setError('Could not load events');
      }
    };
    fetchEvents();
  }, [token]);

  return (
    <div>
      <h2>Events</h2>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <ul>
        {events.map(event => (
          <li key={event.id}>
            {event.name} ({event.timestamp})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EventsPage;
