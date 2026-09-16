
import { useEffect, useRef, useState } from "react";

export const useSpeechToText = (onSilence) => {
  const recognitionRef = useRef(""); // SpeechRecognition
  const slienceTimeRef = useRef("");
  const onSlienceRef = useRef(onSilence);
  const transcriptRef = useRef("");
  const [transcript, setTranscript] = useState("");

  useEffect(() => {
    onSlienceRef.current = onSilence;
  }, [onSilence]);

  useEffect(() => {
    transcriptRef.current = transcript;
  }, [transcript]);

  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("SpeechRecognition is not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continous = true;
    recognition.lang = "en-US";
    recognition.interimResult = true;

    recognition.onresult = (event) => {
      let finalText = "";
      let interimText = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;

        if (result.isFinal) {
          finalText += transcript;
        } else {
          interimText += transcript;
        }
      }

      if (finalText) {
        setTranscript((prev) => (prev + " " + finalText).trim());
      }

      if (finalText || interimText) {
        resetSilenceTimer();
      }
    };

    recognition.onerror = (error) => {
      console.error("SpeechRecognition error", error);
    };

    recognition.start();
    recognitionRef.current = recognition;
  };

  const resetSilenceTimer = () => {
    clearTimeout(slienceTimeRef.current);

    slienceTimeRef.current = setTimeout(() => {
      onSlienceRef.current(transcriptRef.current);
    }, 2000);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    clearTimeout(slienceTimeRef.current);
  };

  return {
    stopListening,
    resetSilenceTimer,
    startListening,
  };
};