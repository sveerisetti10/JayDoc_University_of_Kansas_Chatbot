import { useState, useRef } from 'react';

const QueryBox = () => {
    // Here we initialize the state variables we need for the component. The setQuery function is used to update the query state variable.
    const [query, setQuery] = useState('');
    // Here we initialize the response state variable to store the response we get from the backend. The setResponse function is used to update the response state variable.
    const [response, setResponse] = useState('');
    // Here we initialize the loading state variable to indicate when the query is being submitted. The setLoading function is used to update the loading state variable.
    const [loading, setLoading] = useState(false);
    // Here we use the useRef hook to create a reference to the response box element. This is useful for scrolling the response box to the bottom when the response is updated.
    const responseRef = useRef(null);

    const handleQuerySubmit = async () => {
        // By setting the loading state variable to true, we indicate that the query is being submitted.
        setLoading(true);
        // Here we clear the response state variable to prepare for the new response
        setResponse('');
        // This is where we log the query to the console. This is useful for debugging.
        console.log('Submitting query:', query);
        // This is where we make the API call to the backend. We use the query endpoint which requires a POST request.
        try {
            const res = await fetch('http://localhost:5002/query', {
                method: 'POST',
                // The content type is set to JSON because we are sending a JSON object in the body.
                headers: {
                    'Content-Type': 'application/json',
                },
                // Here we convert the query string to a JSON object and send it in the body of the request.
                body: JSON.stringify({ query }),
            });
            // Here we create some debug logs to help us understand the response we get from the backend.
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            const data = await res.json();
            console.log('Received response:', data);
            setResponse(data.response);
        } catch (error) {
            console.error('Error fetching response:', error);
            setResponse('Error fetching response');
        }
        setLoading(false);
    };

    return (
        <div className="container">
            <div className="query-box">
                <input 
                    type="text" 
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)} 
                    placeholder="Enter your query"
                />
                <button onClick={handleQuerySubmit} disabled={loading}>
                    {loading ? 'Loading...' : 'Submit'}
                </button>
                <div className="response-box" ref={responseRef}>
                    <h3>Response:</h3>
                    {loading ? <p>Loading...</p> : <p>{response}</p>}
                </div>
            </div>
        </div>
    );
};

export default QueryBox;
