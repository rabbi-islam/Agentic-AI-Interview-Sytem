import { useEffect, useState } from "react";
import { APP_CONSTANT } from "../util/constant";
import { reportAPI, submitAPI ,startInterviewAPI, endInterviewAPI} from "../services/interview";
import StartInterview from "../components/StartInterview";
import { playAudio } from "../util/audio";
import Buttons from "../components/Buttons";
import { useSpeechToText } from "../hooks/useSpeechToText";
import Report from "../components/Report";

const InterviewPage = () => {

    const [sessionId, setSessionId] = useState(null);
    const [status, setStatus] = useState(APP_CONSTANT.IDLE);
    const [question, setQuestion] = useState("");
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);


    const onAutoSubmit = async (finalText) => {
      stopListening();
      if (!finalText.trim()) {
        return;
      }

      //submit api calling here
      const payload = {
            "session_id": sessionId,
            "answer": finalText,
            "skip": false
        }
      const data = await submitAPI(payload);

      if(data.interviewEnded) {
            // Report generate
            finshInterview();
        } else {
            // Ask next question
            setQuestion(data.nextQuestion);
            setStatus(APP_CONSTANT.ASKING);
        }

    }
    const {startListening, stopListening} = useSpeechToText(onAutoSubmit);


    const finshInterview = async () => {
        setStatus(APP_CONSTANT.COMPLETED);
        // call report endpoint
        const data = await reportAPI(sessionId);

        if(!data) {
            return;
        }

        setReport(data.result)

    }




    // function to end interview
    const endInterview = async () => {
      stopListening();

      // call end interview api
      await endInterviewAPI(sessionId);
      await finshInterview();
    }


    // function to skip question
        const skipQuestion = async () => {
        // TODO skipQuestion
        stopListening();

        // submit endpoint
        const payload = {
            "session_id": sessionId,
            "answer": "",
            "skip": true
        }
        const data = await submitAPI(payload);

        if(data.interviewEnded) {
            // Report generate
            finshInterview();
        } else {
            // Ask next question
            setQuestion(data.nextQuestion);
            setStatus(APP_CONSTANT.ASKING);
        }
    }


    // we will keep asking question till it is in "ASKING" state
    useEffect(() => {
        if(status === APP_CONSTANT.ASKING) {
            playAudio(question, () => {
                setStatus(APP_CONSTANT.LISTENING);

                //TODO speech to text
                startListening();

            })
        }
    }, [status, question]);

    const startInterview = async () => {

      //start api endpoint call 
      const data =  await startInterviewAPI();


      if(!data){
        console.error("Error starting interview");
        return;
      }

      setSessionId(data.sessionId);
      setQuestion(data.firstQuestion);
      setStatus(APP_CONSTANT.INTRO);


      //play text to speech
      const introText = data.introText;
      playAudio(introText, () =>{
        setStatus(APP_CONSTANT.ASKING);
      })

        
    }

  return <>
    { status === APP_CONSTANT.IDLE && <StartInterview onClick={startInterview } />}
    { (status === APP_CONSTANT.ASKING || status === APP_CONSTANT.LISTENING) && <Buttons skipQuestion={skipQuestion} endInterview={endInterview}/> }
    { status === APP_CONSTANT.COMPLETED && <Report report={report}/> }
  
   </>
}
export default InterviewPage;
