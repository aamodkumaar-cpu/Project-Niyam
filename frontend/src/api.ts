
const API_BASE_URL = "http://localhost:8000/api/v1";

export interface BusinessProfile {
  business_name: string;
  industry: string;
  company_size: string;
  state: string;
}

export interface Source {
  document_id: string;
  source: string;
  page_number: number;
}

export interface QuestionResponse {
  answer: string;
  sources: Source[];
}

export async function configureProfile(
  profile: BusinessProfile,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/profile`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(profile),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Unable to configure business profile (${response.status}).`,
    );
  }
}

export async function askNiyam(
  question: string,
): Promise<QuestionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/questions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Niyam request failed (${response.status}).`,
    );
  }

  return response.json();
}


export interface SourceResponse {
    document_id: string;
    source: string;
    page_number: number;
  }
  
  export interface QuestionResponse {
    answer: string;
    sources: SourceResponse[];
  }
  
  