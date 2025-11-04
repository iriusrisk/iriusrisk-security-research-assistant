import React, { createContext } from 'react';

// ActivityIndicator Context
export const ActivityIndicatorContext = createContext({
  show: () => {},
  hide: () => {}
});

