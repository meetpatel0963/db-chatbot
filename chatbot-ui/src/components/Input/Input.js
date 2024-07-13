import React from "react";
import { TextField } from "@material-ui/core";
import Avatar from "@material-ui/core/Avatar";
import IconButton from "@material-ui/core/IconButton";
import SendIcon from "@material-ui/icons/Send";

import "./Input.css";


// Input Component - A single row with TextField followed by Send Icon Button.
// Props - message: State containing the current Message which user is typing
//       - setMessage: Function callback to change the message state
//       - sendMessage: Function callback to append the message to Messages state array


const Input = ({ message, setMessage, sendMessage }) => {
  return (
    <div className="combine">
      <TextField
        className="input"
        value={message["text"]}
        multiline = {true}
        maxRows = {3}
        fullWidth
        variant="outlined"
        placeholder="Type a message..."
        onChange={(event) =>
          setMessage({ text: event.target.value, sender: "user" })
        }
        // Calling sendMessage on click on Enter Key
        onKeyPress={(event) =>
          event.key === "Enter" ? sendMessage(event) : null
        }
      />
      <div className="avatar-container">
        <Avatar className="button-container">
          <IconButton
            className="icon-button"
            // Calling sendMessage on clicking this button
            onClick={(event) => sendMessage(event)}
          >
            <SendIcon />
          </IconButton>
        </Avatar>
      </div>
    </div>
  );
};

export default Input;
