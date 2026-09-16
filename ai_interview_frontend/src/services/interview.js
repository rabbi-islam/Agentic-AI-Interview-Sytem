
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/interview"; // Replace with your backend API base URL

export const startInterviewAPI = async () => {

    try {

        const response = await axios.get(`${API_BASE_URL}/start`)
        return response.data;
        
    } catch (error) {
        console.error("Error starting interview:", error);
    }

    return null;

}