from fastapi import APIRouter, HTTPException, status

from models.interview import InterviewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.interview_service import create_session, get_session, save_answer

router = APIRouter(
    prefix="/interview",
    tags=["interview"]
)


@router.get("/start")
async def start_interview():

     questions = [
        "What is your name?",
        "What is your age?",
        "What is your favorite programming language?",
        "What is your experience with Python?",
        "What is your experience with FastAPI?",
        "What is your experience with REST APIs?",
     ]
     session = create_session()
     session.questions = questions

     return{
          "introText": "Welcome to the interview! Please answer the following questions.",
          "sessionId": session.session_id,
          "firstQuestion": questions[0]
     }



@router.post("/submit", response_model = AnswerResponse)
async def submit_answer(answerReq: AnswerRequest):

     #check if session exists
     session = get_session(answerReq.session_id)
     if not session or session.status == InterviewStatusEnum:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session not found or already completed")


     #save the answer to the session
     save_answer(answerReq.answer , answerReq.skip, session)

     #return the next question or a message indicating the interview is complete
     if session.status == InterviewStatusEnum.COMPLETED:
          return {
               "interviewEnded":True
          }
     return {
          "interviewEnded":False,
          "nextQuestion": session.questions[session.current_index]
     }


@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    session.status = InterviewStatusEnum.COMPLETED

    return {
            "interviewEnded": True
    }


@router.get("/report/{session_id}")
async def report(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    return {
          "result":  "you Interviewr report" 

     }