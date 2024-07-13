import React from "react";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import ContactSupportIcon from "@material-ui/icons/ContactSupport";
import HelpIcon from '@material-ui/icons/Help';

import "./InfoBar.css";

// InfoBar Component
const ButtonAppBar = () => {
  return (
    <div>
      <AppBar position="static" className="infoBar">
        <Toolbar>
          <ContactSupportIcon className="largeIcon"> </ContactSupportIcon>
          <h2 className="heading margin-left-4"> ChatBot </h2>

        </Toolbar>
      </AppBar>
    </div>
  );
};

export default ButtonAppBar;