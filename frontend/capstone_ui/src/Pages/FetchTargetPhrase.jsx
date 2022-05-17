import React from "react";
import ReactDOM from "react-dom";
import Highlighter from "react-highlight-words";


/*
Description: This class will call the API that fetches target phrases from AWS server
*/
class FetchTargetPhrase extends React.Component {
    // Constructor
	constructor(props) {
		super(props);

		this.state = {
			targetPhraseData: null,
            renderAgain: false
		};

        this.getTargetPhrase = this.getTargetPhrase.bind(this);
        this.updateTargetPhraseData = this.updateTargetPhraseData.bind(this);
	}

    updateTargetPhraseData (data){
		this.setState({targetPhraseData: data});
		console.log(this.state.targetPhraseData);
	}
    async getTargetPhrase(requestOptions) {
        let response = await fetch('http://cs4470capstone-env.eba-f9wabacx.us-east-1.elasticbeanstalk.com/requirements', requestOptions)
        let data = await response.json()
        console.log(data);
        this.updateTargetPhraseData(data);
        return data;
    }


    componentDidMount() {
        const requestOptions = {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
            },
            body: JSON.stringify({ title: 'Target Phrase' })
        };
		
		this.getTargetPhrase(requestOptions);
        console.log(this.state.targetPhraseData);
        this.setState({renderAgain: true});
		
	}
	
	render() {
		if (!this.state.renderAgain) 
			return <div>
				<h1> Loading 1.... </h1> 
			</div> 
		return (
			<div>
                <h1> Fetched </h1> 
                {/* <Highlighter
                    highlightClassName="YourHighlightClass"
                    searchWords={this.state.targetPhraseData}
                    autoEscape={true}
                    textToHighlight="The dog is chasing the cat. Or perhaps they're just playing?"
                />, */}
            </div>
	);


    }
}

export default FetchTargetPhrase;
