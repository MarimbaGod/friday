import React, { useRef, useState } from 'react';
import { Button } from '@chakra-ui/react';

const AudioRecorder = ({ onAudioRecorded }) => {
    const [recording, setRecording] = useState(false);
    const mediaRecorder = useRef(null);
    let audioChunks = useRef([]);

    const startRecording = () => {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder.current = new MediaRecorder(stream);
                audioChunks.current = []; //resets chunks for new rec

                mediaRecorder.current.ondataavailable = event => {
                    audioChunks.current.push(event.data);
                    console.log("Data available: ", event.data.size); //check chunk size
                };

                mediaRecorder.current.onstop = () => {
                    console.log("recording actually stopped");
                    const audioBlob = new Blob(audioChunks.current, { type: 'audio/mpeg' });
                    console.log("Recording stopped, blob size: ", audioBlob.size);
                    onAudioRecorded(audioBlob); //pass blob to parent
                };

                mediaRecorder.current.start();
                console.log("Recording started");
                setRecording(true);
            })
            .catch(error => {
                console.error("Error accessing media devices", error);
            });
    };

    const stopRecording = () => {
        console.log("attempting to stop recording", mediaRecorder.current?.state); //debug
        if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
            mediaRecorder.current.stop();
            setRecording(false);
        }
    };

    const toggleRecording = () => {
        console.log("Current recording state before toggle:", recording);
        if (recording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    return (
        <Button colorScheme="teal" onClick={toggleRecording}>
            {recording ? 'Stop Recording' : 'Start Recording'}
        </Button>
    );

};

export default AudioRecorder;
