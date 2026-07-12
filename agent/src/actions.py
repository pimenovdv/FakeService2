from typing import List, Dict, Any

class AgentActions:
    """
    Simulates actions the frontend normally performs by making API calls to the backend.
    """

    @staticmethod
    async def fetch_autocomplete_options(client, data_source: str, query: str) -> List[Dict[str, Any]]:
        """
        Fetches options from the autocomplete data source and filters them by the query string.
        """
        response = await client.get(f"/api/data/{data_source}")
        response.raise_for_status()
        options = response.json()

        # Assume the list contains dicts with 'id' and 'name' or 'label'
        filtered_options = []
        q = query.lower()
        for opt in options:
            label = str(opt.get('name', opt.get('label', opt.get('text', '')))).lower()
            if q in label:
                filtered_options.append(opt)

        return filtered_options

    @staticmethod
    async def simulate_form_submission(client, service_id: str, current_screen_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submits form data to the next_step endpoint, mimicking a frontend form submission.
        """
        payload = {
            "service_id": service_id,
            "current_screen_id": current_screen_id,
            "answers": answers
        }

        response = await client.post("/api/screens/next_step", json=payload)
        response.raise_for_status()
        return response.json()
