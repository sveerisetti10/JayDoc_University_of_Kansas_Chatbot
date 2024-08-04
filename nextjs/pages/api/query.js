export default async function handler(req, res) {
    // Here we define the API endpoint to only accept POST requests
    if (req.method === 'POST') {
        const { query } = req.body;
        console.log('API received query:', query);
        try {
            const response = await fetch('http://localhost:5002/query', {  // Here we define the port as 5002
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });
            const data = await response.json();
            // Here we add some debugging information to tell us what the API received from Flask
            console.log('API received response from Flask:', data);
            res.status(200).json(data);
        } catch (error) {
            // Here we add some debugging information to tell us what the error is
            console.error('API error:', error);
            res.status(500).json({ error: 'Error fetching response' });
        }
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}
