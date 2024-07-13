import React from "react";
import Message from "../Message/Message";
import AutoScroll from './AutoScroll';

import "./Messages.css";


// Messages Component
const Messages = ({ messages, searchType, setSearchType, setMessages }) => (
  // Pass each message in messages array yo the Message Component
  <div className="messages">
      {messages.map((message, i) => (
        <div key={i} className="message-vertical-margin" >
          <Message message={message} searchType={searchType} setSearchType={setSearchType} messages={messages} setMessages={setMessages} />
        </div>
      ))}
      <AutoScroll />
  </div>
);

export default Messages;
