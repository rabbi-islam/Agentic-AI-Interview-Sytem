const Buttons = ({ skipQuestion, endInterview }) => {
    return <>
        <button onClick={skipQuestion}>Skip Question</button>
        <button onClick={endInterview}>End Interview</button> 

    </>
}

export default Buttons