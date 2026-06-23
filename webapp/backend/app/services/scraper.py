import traceback

from scrapegraphai.graphs import SmartScraperGraph

from .. import schemas
from . import logging_service

LOG = "scraper"


def run_scrape(req: schemas.ScrapeRequest) -> schemas.ScrapeResponse:
    llm_id = f"{req.llm.provider}/{req.llm.model}"
    logging_service.info(LOG, f"Starting scrape: source={req.source} llm={llm_id} backend={req.backend.type.value}")

    try:
        llm_config = {
            "model": llm_id,
            "model_tokens": req.llm.model_tokens,
        }
        if req.llm.api_key and req.llm.provider != "ollama":
            api_key_field = f"{req.llm.provider}_api_key"
            llm_config[api_key_field] = req.llm.api_key
            logging_service.debug(LOG, f"Using {req.llm.provider} LLM with API key")

        graph_config: dict = {
            "llm": llm_config,
            "headless": req.backend.headless,
        }

        if req.backend.proxy:
            graph_config["loader_kwargs"] = {"proxy": req.backend.proxy}
            logging_service.debug(LOG, "Proxy configured")

        if req.backend.type in ("crawl4ai", "obscura"):
            exp_cfg: dict = {"backend": req.backend.type.value}
            if req.backend.type == "crawl4ai" and req.backend.crawl4ai:
                exp_cfg["crawl4ai"] = req.backend.crawl4ai.model_dump(exclude_none=True)
                logging_service.debug(LOG, f"Crawl4AI config: {exp_cfg['crawl4ai']}")
            elif req.backend.type == "obscura" and req.backend.obscura:
                exp_cfg["obscura"] = req.backend.obscura.model_dump(exclude_none=True)
                logging_service.debug(LOG, f"Obscura config: {exp_cfg['obscura']}")
            graph_config["experimental"] = exp_cfg

        graph = SmartScraperGraph(
            prompt=req.prompt,
            source=req.source,
            config=graph_config,
        )

        result = graph.run()
        logging_service.info(LOG, f"Scrape completed successfully for {req.source}")
        logging_service.debug(LOG, f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result).__name__}")

        return schemas.ScrapeResponse(
            status="success",
            data=result,
            execution_info=graph.get_execution_info(),
        )

    except Exception as exc:
        logging_service.error(LOG, f"Scrape failed for {req.source}: {exc}", exc=exc)
        return schemas.ScrapeResponse(
            status="error",
            error=f"{type(exc).__name__}: {exc}",
            execution_info={"traceback": traceback.format_exc()},
        )
