import { useEffect, useState } from "react";
import { APP_CONSTANT } from "../util/constant";
import {startInterviewAPI} from "../services/interview";
import StartInterview from "../components/StartInterview";
import { playAudio } from "../util/audio";
import Buttons from "../components/Buttons";

const InterviewPage = () => {

    const [sessionId, setSessionId] = useState(null);
    const [status, setStatus] = useState(APP_CONSTANT.IDLE);
    const [question, setQuestion] = useState("");
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);


    // function to skip question
    const skipQuestion = () => {}

    // function to end interview
    const endInterview = () => {}

    // we will keep asling question till it is in "ASKING" state
    useEffect(() => {
        if(status === APP_CONSTANT.ASKING) {
            playAudio(question, () => {
                setStatus(APP_CONSTANT.LISTENING);

                //TODO speech to text

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
    { status === APP_CONSTANT.ASKING && APP_CONSTANT.LISTENING && <Buttons skipQuestion={skipQuestion} endInterview={endInterview} /> }
  
   </>
}
export default InterviewPage;
