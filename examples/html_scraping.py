import os
from dotenv import load_dotenv
from yosoai import send_request

load_dotenv()

query_info = '''
        Given this code extract all the information in a json format about the news.
        <article class="c-card__wrapper aem_card_check_wrapper" data-cardindex="0">
            <div class="c-card__content">
                <h2 class="c-card__title">Booker show with 52 points, whoever has the most games over 50</h2>
                <div class="c-card__label-wrapper c-label-wrapper">
                    <span class="c-label c-label--article-heading">Standings</span>
                </div>
                <p class="c-card__abstract">The Suns' No. 1 dominated the match won in New Orleans, scoring 52 points. It's about...</p>
                <div class="c-card__info">
                    <time class="c-card__date" datetime="20 gen - 07:54">20 gen - 07:54</time>
                    <span class="c-card__content-data">
                        <i class="icon icon--media-outline icon--gallery-outline icon--xxsmall icon--c-neutral">
                            <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" class="icon__svg icon__svg--gallery-outline">
                                <path d="M26.174 32.174v31.975h44.588V32.174H26.174zm-3.08-9.238h50.747A6.159 6.159 0 0 1 80 29.095v38.134a6.159 6.159 0 0 1-6.159 6.158H23.095a6.159 6.159 0 0 1-6.159-6.158V29.095a6.159 6.159 0 0 1 6.159-6.159zM9.239 55.665a4.619 4.619 0 0 1-9.238 0V16.777C0 10.825 4.825 6 10.777 6H64.08a4.619 4.619 0 1 1 0 9.238H10.777c-.85 0-1.54.69-1.54 1.54v38.887z" fill="currentColor" fill-rule="evenodd"></path>
                            </svg>
                        </i>
                        28 foto
                    </span>
                </div>
            </div>
            <div class="c-card__img-wrapper">
                <figure class="o-aspect-ratio o-aspect-ratio--16-10 ">
                    <img crossorigin="anonymous" class="c-card__img j-lazyload" alt="Partite con 50+ punti: Booker in Top-20" data-srcset="..." sizes="..." loading="lazy" data-src="...">
                    <noscript>
                        <img crossorigin="anonymous" class="c-card__img" alt="Partite con 50+ punti: Booker in Top-20" srcset="..." sizes="..." src="...">
                    </noscript>
                </figure>
                <i class="icon icon--media icon--gallery icon--medium icon--c-primary">
                    <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" class="icon__svg icon__svg--gallery">
                        <path d="M17.005 20.221h60.211c1.538 0 2.784 1.28 2.784 2.858v48.317c0 1.578-1.246 2.858-2.784 2.858H17.005c-1.537 0-2.784-1.28-2.784-2.858V23.079c0-1.578 1.247-2.858 2.784-2.858zM5.873 11.873V60.62a2.937 2.937 0 0 1-5.873 0V11.286A5.286 5.286 0 0 1 5.286 6h61.08a2.937 2.937 0 1 1 0 5.873H5.873z"></path>
                    </svg>
                </i>
            </div>
        </article>
    '''

def main():
    # Get OpenAI API key from environment variables
    openai_key = os.getenv("API_KEY")
    if not openai_key:
        print("Error: OpenAI API key not found in environment variables.")
        return

    # Example values for the request
    request_settings = [
        {
            "title": "title",
            "type": "str",
            "description": "Title of the news"
        }
    ]

    # Choose the desired model and other parameters
    selected_model = "gpt-3.5-turbo"
    temperature_value = 0.7

    # Invoke send_request function
    result = send_request(openai_key, query_info, request_settings, selected_model, temperature_value, 'cl100k_base')

    # Print or process the result as needed
    print("Result:", result)

if __name__ == "__main__":
    main()