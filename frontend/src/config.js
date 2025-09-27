// used to backend app url for local development or deployed via heroku

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';


export default API_BASE_URL;