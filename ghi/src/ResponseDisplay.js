import React, { useState } from 'react';
import { Text, Box, Audio } from '@chakra-ui/react';

const ResponseDisplay = ({ response }) => {
    return (
        <Box>
            <Text fontSize="lg">{response.text_response}</Text>
            {response.audio_url && (
                <audio controls src={`http://localhost:8000${response.audio_url}`}>
                    Your browser does not support the audio element
                </audio>
            )}
        </Box>
    );
};

export default ResponseDisplay;
