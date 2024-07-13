import React from "react";
import { BrowserRouter as Router, Route } from "react-router-dom";

import Chat from "./components/Chat/Chat";

// App Component - A single route '/' leading to Chat component.
const App = () => {
  return (
    <Router>
      <Route path="/" component={Chat} />
    </Router>
  );
};

export default App;

