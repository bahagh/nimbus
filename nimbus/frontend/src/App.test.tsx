import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Nimbus API Demo title', () => {
  render(<App />);
  expect(screen.getByText(/Nimbus API Demo/i)).toBeInTheDocument();
});
