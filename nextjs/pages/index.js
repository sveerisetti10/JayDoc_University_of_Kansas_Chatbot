import QueryBox from '../components/QueryBox';

export default function Home() {
    return (
        <div className="container">
            <div className="content">
                <h1>JayDoc Helper!</h1>
                <div className="sandbox">
                    <p>Instructions: Enter your query regarding the JayDoc Free Health Clinic in the box below and click 'Submit' to receive a response.</p>
                </div>
                <QueryBox />
            </div>
            <img src="/jaydoc_mascot.png" alt="Jayhawk" className="jayhawk-image" />
        </div>
    );
}
