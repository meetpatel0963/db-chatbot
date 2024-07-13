// import required libs, components and css
import React, { useState, useEffect } from "react";
import axios from "axios";

import InfoBar from "../InfoBar/InfoBar";
import Messages from "../Messages/Messages";
import Input from "../Input/Input";
import { BERT_SERVER_URL, WAITING_MESSAGE } from "../../config/config";

import "./Chat.css";


// Chat Component
const Chat = () => {
  /*
    States:
      - message: current value of message
      - messages: an array to keep track of all the messages
  */

    

  const [message, setMessage] = useState({ text: "", sender: "user" });
  const [messages, setMessages] = useState([{text:"Hello",sender:"bot"}]);
  const [searchType, setSearchType] = useState("");
  const [confluenceJiraUsername, setConfluenceJiraUsername] = useState("");
  const [confluenceJiraPassword, setConfluenceJiraPassword] = useState("");
  const [bitBucketUsername, setBitBucketUsername] = useState("");
  const [bitBucketPassword, setBitBucketPassword] = useState("");
  const [domain, setDomain] = useState("");
  const [project, setProject] = useState("");
  const [currentQuestion,setCurrentQuestion] = useState(0);
  const [currentAnswer,setCurrentAnswer] = useState(0);
  const [currentAction,setCurrentAction] = useState(null);
  const [initial,setInitial] = useState(false);


  // Array of object containing state and corresponding question for changing the state

// console.log("Current Action:",currentAction);

  const series = [
    {
      question:'Please Enter Confluence/Jira Username',
      state: 'confluenceJiraUsername',
    },
    {
      question:'Please Enter Confluence/Jira password',
      state:'confluenceJiraPassword',
    },
    {
      question:'Please Enter Bit Bucket Username',
      state:'bitBucketUsername',
    }, 
    {
      question:'Please Enter Bit Bucket password',
      state:'bitBucketPassword',
    },
    {
      question:'Please Enter search type',
      state:'searchType',
    },    
    {
      question:'Please Enter domain',
      state:'domain',
    }, 
    {
      question:'Please Enter Project',
      state:'project',
    },
  ];

  // Object containing the setState method corresponding to each state
  const stateSetters = {
    confluenceJiraUsername: setConfluenceJiraUsername,
    confluenceJiraPassword: setConfluenceJiraPassword,
    bitBucketUsername: setBitBucketUsername,
    bitBucketPassword: setBitBucketPassword,
    searchType:setSearchType,
    domain:setDomain,
    project:setProject,
  };


  // Object containing reset actions corresponding to array of actions to perform
  const resetActions = {
    '/resetJira':[0,1,4,5,6],
    '/resetBitBucket':[2,3,4,5,6],
    '/resetSearchType':[4,5,6],
    '/resetDomain':[5,6],
    '/resetProject':[6],
  };

  const doc_retriever_map = {
    'confluence': {
      'username': confluenceJiraUsername,
      'password': confluenceJiraPassword
    },
    'jira': {
      'username': confluenceJiraUsername,
      'password': confluenceJiraPassword
    },
    'bitbucket': {
      'username': bitBucketUsername,
      'password': bitBucketPassword
    }
  };

  const AppendMessage = (text,sender,hidden = false) => {
    setMessages([...messages,{text,sender,hidden}]);
  };

  const printSuccessMessage = () => {
    AppendMessage("Your details have been saved. Now you can ask your queries.", "bot");
  };

  console.log(confluenceJiraUsername, confluenceJiraPassword, bitBucketUsername, bitBucketPassword, searchType, domain, project);
  
  // UseEffect to be called when a message is send by bot or user
  useEffect(() => {

    let seriesLength = series.length;

    //Taking Last Message
    const lastMessage = messages.slice(-1)[0];
    
    // Only set answer and render next question if the last message is send by user
    if(currentAnswer < seriesLength && lastMessage.sender === "user" && !initial){

      //Sending the question 
      if(currentQuestion < seriesLength){
        setMessages([...messages,{ text:series[currentQuestion].question, sender:"bot" }]);
        setCurrentQuestion(currentQuestion+1);
      }

      //Storing the answer in corresponding state
      if(currentQuestion > 0){
        stateSetters[series[currentAnswer].state](lastMessage.text);
        if(currentAnswer === (seriesLength-1)){
          printSuccessMessage();
          setInitial(true);
        }
        setCurrentAnswer(currentAnswer+1);
      }
    }
    else if(lastMessage.sender === "user"){
  
      let isRestartFlag = false;
      for(let key in resetActions){
        if(String(key) === String(lastMessage.text)){
          isRestartFlag = true;
          break;
        }
      }
      if(isRestartFlag){
        setCurrentAction(lastMessage);
        setCurrentQuestion(0);
        setCurrentAnswer(0);
        let actions = resetActions[lastMessage.text];
        for(let i=0;i<actions.length;i++){
          stateSetters[series[actions[i]].state]("");
        }
        AppendMessage("Hello","user",true);
      }
      else{
        if(currentAction){
          let actions = resetActions[currentAction.text];
          if(currentAnswer < actions.length && lastMessage.sender === "user"){

            //Sending the question 
            if(currentQuestion < actions.length){
              AppendMessage(series[actions[currentQuestion]].question,"bot");
              setCurrentQuestion(currentQuestion+1);
            }

            //Storing the answer in corresponding state
            if(currentQuestion > 0){
              stateSetters[series[actions[currentAnswer]].state](lastMessage.text);
              if (currentAnswer + 1 === actions.length){
                printSuccessMessage();
                setCurrentAction(null);
              }
              setCurrentAnswer(currentAnswer+1);
            }
          }
        }
        else{
          setMessages([...messages, { text: WAITING_MESSAGE, sender: "bot" }]);
          let searchTypeKey = searchType.toLowerCase();
          let domainKey = domain.toLowerCase();
          let projectKey = project.toLowerCase();
          
          axios
            .get(`${BERT_SERVER_URL}?confluence_username=${confluenceJiraUsername}&confluence_password=${confluenceJiraPassword}&bitbucket_username=${bitBucketUsername}&bitbucket_password=${bitBucketPassword}&question=${lastMessage.text}&doc_retriever_key=${searchTypeKey}&domain=${domainKey}&projectkey=${projectKey}`)
            .then((response) => {
              const reply = response.data.answers[0].answer;
              let newMessages = messages.filter((m) => m["text"] !== WAITING_MESSAGE)
              setMessages([...newMessages, { text: reply, sender: "bot" }]);
            })
            .catch((error) => {
              console.log(error);
            });          
        }      
      }
    }
  }, [messages]);

  // If user clicks on the send button or enter key, sendMessage is called.
  const sendMessage = (event) => {
    // To stop the default reloading of the browser page.
    event.preventDefault();

    // If message is not empty and sender is not a bot, add it to messages array and set message to empty.
    if (message["text"] !== "" && message["sender"] !== "bot") {
      setMessages([...messages, message]);
      setMessage({ text: "", sender: "user" });
    }
  };
  
  // Returns a Chat component with InfoBar at the Top followed by Messages and Input components.
  return (
    <div className="outerContainer">
      <div className="container">
        <InfoBar />
        <Messages messages={messages} searchType={searchType} setSearchType={setSearchType} setMessages={setMessages} />
        <Input
          message={message}
          setMessage={setMessage}
          sendMessage={sendMessage}
        />
      </div>
    </div>
  );
};

export default Chat;