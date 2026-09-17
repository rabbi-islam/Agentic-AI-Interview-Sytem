from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.interview import InterviewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.ai_service import generate_questions_intro, generate_report
from services.interview_service import create_session, get_session, save_answer
from util.file_util import validate_file, extract_text

router = APIRouter(
    prefix="/interview",
    tags=["interview"]
)


@router.post("/generate_question")
async def generate_questions(
     job_title: str = Form(...),
     job_description: str = Form(...),
     resume: UploadFile = File(...)
):
     #validate resume file
     await validate_file(resume)

     #extract text from resume
     resume_text = await extract_text(resume)

     #generate questions based on job title, job description and resume text
     resp = await generate_questions_intro(job_title = job_title, job_description = job_description, resume_text = resume_text)

     session = create_session()
     session.questions = resp.get("questions")
     session.introText = resp.get("introText")

     #print("Result>>>>>:", resp)

     return{"sessionId": session.session_id,}

@router.get("/start/{session_id}")
async def start_interview(session_id: str):

     #check if session exists
     session = get_session(session_id)
     if not session or session.status == InterviewStatusEnum:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session not found or already completed")

     return{
          "introText": session.introText,
          "firstQuestion": session.questions[0]
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
    
    resp = await generate_report(session.answers)

    return {"Result:": resp  }