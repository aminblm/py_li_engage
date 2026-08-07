import asyncio
import sys
from py_li_engage.config import ConfigLoader, MACRO_BREAK_MAX_MS, MACRO_BREAK_MIN_MS, logger
from py_li_engage.services import BrowserSessionManager, GroqService, HumanBehaviorUtility
from py_li_engage.workflow_elements import (
    ExtractPostContentElement,
    ExtractPostUrlElement,
    LikePostElement,
    MultiProfileAutomationElement,
    PublishCommentElement,
)


class WorkflowOrchestrator:

    @staticmethod
    async def run() -> None:
        logger.info("[Workflow] Starting Execution Pipeline...")
        browser_instance = None
        global_pipeline_summary: list[dict[str, str | int | None | dict[str, str]]] = []

        try:
            logger.info("[Workflow] Step 1: Loading configuration and target URLs...")
            api_key = ConfigLoader.load_api_key()
            target_urls = ConfigLoader.load_target_urls()

            logger.info("[Workflow] Step 2: Initializing browser session...")
            browser, _context, page = await BrowserSessionManager.initialize()
            browser_instance = browser

            extract_url_element = ExtractPostUrlElement()
            extract_content_element = ExtractPostContentElement()
            like_post_element = LikePostElement()
            publish_comment_element = PublishCommentElement()
            multi_profile_element = MultiProfileAutomationElement()

            link_index = 0
            for target_url in target_urls:
                link_index += 1
                logger.info(f"[Workflow] --------------------------------------------------")
                logger.info(f"[Workflow] Processing Target Link [{link_index} of {len(target_urls)}]: {target_url}")
                logger.info(f"[Workflow] --------------------------------------------------")

                link_execution_record: dict[str, str | int | None | dict[str, str]] = {
                    "targetUrl": target_url,
                    "linkIndex": link_index,
                    "status": "success",
                    "postUrl": None,
                    "commentGenerated": None,
                    "likeStatus": None,
                    "multiProfileStats": None,
                    "error": None,
                }

                try:
                    logger.info("[Workflow] Step 3: Extracting post URL from target profile...")
                    post_url = await extract_url_element.execute(page, target_url)
                    link_execution_record["postUrl"] = post_url

                    logger.info("[Workflow] Step 4: Extracting post content...")
                    post_content = await extract_content_element.execute(page, post_url)

                    logger.info("[Workflow] Step 5: Generating short comment via Groq...")
                    short_comment = await GroqService.generate_comment(api_key, post_content)
                    link_execution_record["commentGenerated"] = short_comment
                    logger.info(f'[Workflow] Generated Short Comment: "{short_comment}"')

                    logger.info("[Workflow] Step 6: Liking post if not already liked...")
                    like_status = await like_post_element.execute(page)
                    link_execution_record["likeStatus"] = like_status

                    logger.info("[Workflow] Step 7 & 8: Inserting and publishing comment...")
                    await publish_comment_element.execute(page, short_comment)

                    logger.info("[Workflow] Step 9: Executing multi-profile automation...")
                    multi_profile_stats = await multi_profile_element.execute(page)
                    link_execution_record["multiProfileStats"] = multi_profile_stats

                    logger.info(f"[Workflow] Successfully completed pipeline iteration for target URL: {target_url}")
                except Exception as url_iteration_error:
                    link_execution_record["status"] = "skipped_or_failed"
                    link_execution_record["error"] = str(url_iteration_error)
                    logger.warning(f"[Workflow Notice] Skipping URL {target_url} due to error: {url_iteration_error}")
                finally:
                    global_pipeline_summary.append(link_execution_record)
                    logger.info(f"[Workflow Intermediary Progress Report] Finished processing link {link_index}/{len(target_urls)}")

                    if link_index < len(target_urls):
                        await HumanBehaviorUtility.random_macro_break(MACRO_BREAK_MIN_MS, MACRO_BREAK_MAX_MS)

            logger.info("================================================================")
            logger.info("            FINAL PIPELINE EXECUTION STATISTICS & STATES        ")
            logger.info("================================================================")
            
            for summary_item in global_pipeline_summary:
                logger.info(f"--- Link Report #{summary_item['linkIndex']} ---")
                logger.info(f"Target URL: {summary_item['targetUrl']}")
                logger.info(f"Target Post URL: {summary_item['postUrl'] or 'N/A'}")
                logger.info(f"Execution Status: {summary_item['status']}")
                logger.info(f"Comment Delivered: \"{summary_item['commentGenerated'] or 'None'}\"")
                logger.info(f"Initial Like Status: {summary_item['likeStatus'] or 'N/A'}")
                logger.info(f"Multi-Profile States & Reposts Delivered: {summary_item['multiProfileStats'] or 'N/A'}")
                if summary_item["error"]:
                    logger.info(f"Encountered Error: {summary_item['error']}")
            
            logger.info("================================================================")
            logger.info("[Workflow] Pipeline executed successfully across all target URLs.")
        except Exception as error:
            logger.error(f"[Workflow Error] Pipeline critical failure: {error}", exc_info=True)
            sys.exit(1)
        finally:
            try:
                if browser_instance:
                    logger.info("[Workflow] Cleaning up: Closing browser instance.")
                    await browser_instance.close()
            except Exception as cleanup_error:
                logger.error(f"[Workflow Error] Failed to close browser cleanly: {cleanup_error}")
            logger.info("[Workflow] Execution Pipeline terminated.")


if __name__ == "__main__":
    asyncio.run(WorkflowOrchestrator.run())