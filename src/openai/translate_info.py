#src/openai/translate_info.py
from fastapi import APIRouter, HTTPException
from src.getinfo.rpatools.py import info
from src.openai.openai_service import translate_to_korean

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.get("/translate/")
async def info_result(cve_code:str):
    try:
        result = await info(cve_code) #cve 정보수집

        #한글로번역기능
        if 'descriptions' in result.get('nvd',{}):
            result['nvd']['descriptions'] = await translate_to_korean(result['nvd']['descriptions'])

        return {"info": result}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpectied error: {str(e)}")
        
