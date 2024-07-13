import React from "react";
import ReactEmoji from "react-emoji";
import Loader from "react-loader-spinner";
import Button from '@material-ui/core/Button';

import { WAITING_MESSAGE, SEARCH_TYPE_MESSAGE, SEARCH_TYPES } from "../../config/config";

import "./Message.css";

// Message Component
const Message = ({ message, searchType, setSearchType, messages, setMessages }) => {

  const hiddenMessage = message.hidden ? "hide-message" : "";
  const handleClick = (currentSearchType) => {
    setSearchType(currentSearchType);
    setMessages([...messages, { text: currentSearchType, sender: "user" }]);
  };

  // If the sender is not bot - (sender = 'user'), then align message to the right;
  // If the sender is bot, then align message to the left.
  // While waiting for the bot's reply, show bitloader.
  // If asking for SEARCH_TYPE show buttons. As soon as user selects an option or type something on the textfield, disable all the buttons.

  return message["sender"] !== "bot" ? (
    <div className={`messageContainer ${hiddenMessage} alignCenter justifyEnd`}>
      <div className="messageBox backgroundBlue">
        <p className="messageText colorWhite">
          {ReactEmoji.emojify(message["text"])}
        </p>
      </div>
      <img className="chatAvatar" src="https://img.icons8.com/plasticine/64/000000/user.png" alt="chatbot avatar" />
    </div>
  ) : message["text"] === WAITING_MESSAGE ? (
    <div className="messageContainer justifyStart">
      <div className="messageBox backgroundLight">
        <Loader type="ThreeDots" color="#2979ff" height={60} width={60} />
      </div>
    </div>
  ) : (
    <div className="messageContainer alignCenter justifyStart">
      <img className="chatAvatar" src="https://img.icons8.com/dusk/64/000000/bot--v2.png" alt="user avatar" />
      <div style={{ width: "100%" }}>
        <div className="messageBox backgroundLight marginLeft-1">
          <p className="messageText colorDark">
            {ReactEmoji.emojify(message["text"])}
          </p>
        </div>
        <div className="messageButton">
          {message["text"] === SEARCH_TYPE_MESSAGE ? (
            SEARCH_TYPES.map((currentSearchType, i) => (
              <Button key={i} variant="contained" color="primary" style={{ margin: "5px" }} onClick={() => handleClick(currentSearchType)} disabled={searchType !== ""} >{currentSearchType}</Button>
            ))
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default Message;
