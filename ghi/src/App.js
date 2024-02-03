import React, { useEffect, useState } from "react";
import { ChakraProvider, theme } from '@chakra-ui/react';
import AudioRecorder from './AudioRecorder';
import ResponseDisplay from './ResponseDisplay'
import "./App.css";

function App() {
  const [fridayResponse, setFridayResponse] = useState(null);
  const [responseText, setResponseText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');

  const handleAudioSubmission = async (audioBlob) => {
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "audio.mp3");

    try {
      // transcribe input
      const transcriptionResponse = await fetch('http://localhost:8000/friday/input', {
        method: 'POST',
        body: formData,
      });
      if (!transcriptionResponse.ok) throw new Error('Network response was not ok');

      const transcribedText = await transcriptionResponse.text();
      //do something with the text

      const askFridayResponse = await fetch('http://localhost:8000/friday', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: transcribedText, conversation_history: "[]" }),
      });
      if (!askFridayResponse.ok) throw new Error('askFriday response not ok');
      // Process response from askFriday
      const fridayResponseData = await askFridayResponse.json();

      // use Friday's Response
    } catch (error) {
      console.error("Error submitting audio:", error);
    }
  };

  return (
    <ChakraProvider theme={theme}>
      <AudioRecorder onAudioRecorded={handleAudioSubmission} />
      {fridayResponse && <ResponseDisplay response={fridayResponse} />}
    </ChakraProvider>
  );
};

export default App;
