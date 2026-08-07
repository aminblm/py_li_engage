from .config import (
    NAVIGATION_TIMEOUT_MS,
    PAGE_LOAD_WAIT_MS,
    SLEEP_SHORT_MS,
    SLEEP_LIKE_MS,
    SLEEP_INSERT_MS,
    SLEEP_PUBLISH_MS,
    SLEEP_MODAL_MS,
    SLEEP_CONTEXT_MS,
    SELECTORS,
    logger,
)
from .services import HumanBehaviorUtility
from playwright.async_api import Page


class BaseWorkflowElement:

    def __init__(self, name: str):
        self.name = name

    async def clear_page_state(self, page: Page) -> None:
        try:
            await page.evaluate(
                """() => {
                    localStorage.clear();
                    sessionStorage.clear();
                }"""
            )
        except Exception:
            pass

    async def execute(self, page: Page, *args, **kwargs) -> str | dict[str, str] | None:
        raise NotImplementedError("Method 'execute()' must be implemented by subclass.")


class ExtractPostUrlElement(BaseWorkflowElement):

    def __init__(self):
        super().__init__("ExtractPostUrlElement")

    async def execute(self, page: Page, target_url: str) -> str:
        logger.info(f"Extracting latest post URL from profile: {target_url}")
        await self.clear_page_state(page)

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
        except Exception:
            logger.warning("Navigation timeout reached during profile load, continuing execution...", extra={"targetUrl": target_url})

        await HumanBehaviorUtility.stochastic_sleep(PAGE_LOAD_WAIT_MS)
        await HumanBehaviorUtility.human_scroll_scan(page)

        share_btn_exists = await page.query_selector(SELECTORS["SHARE_BUTTON"])
        if not share_btn_exists:
            raise RuntimeError("Share button not found on profile. Skipping target link.")

        await HumanBehaviorUtility.smooth_scroll_to_element(page, SELECTORS["SHARE_BUTTON"])

        await page.evaluate(
            """(selectors) => {
                const shareBtn = document.querySelector(selectors.SHARE_BUTTON);
                if (shareBtn) shareBtn.click();
            }""",
            SELECTORS,
        )

        await HumanBehaviorUtility.stochastic_sleep(1000)

        post_url = await page.evaluate(
            """async (selectors) => {
                const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
                let copyLinkButton = null;
                const startTime = Date.now();
                while (Date.now() - startTime < 8000) {
                    copyLinkButton = Array.from(document.querySelectorAll(selectors.COPY_LINK_CANDIDATE)).find(el => {
                        const text = el.textContent ? el.textContent.trim().toLowerCase() : '';
                        return text.includes('copy link') || text.includes('copy url') || text.includes('link to post');
                    });
                    if (copyLinkButton) break;
                    await sleep(500);
                }

                if (!copyLinkButton) throw new Error("Copy link button not found.");
                
                const targetEl = copyLinkButton.closest('button, div[role="button"], a, li') || copyLinkButton;
                targetEl.click();
                await sleep(1500);

                const linkElement = document.querySelector(selectors.POST_URL_MODAL);
                if (!linkElement) throw new Error("Target href element not found.");

                const targetPostUrl = linkElement.getAttribute('href');
                if (!targetPostUrl) throw new Error("Target href link is empty.");

                return targetPostUrl;
            }""",
            SELECTORS,
        )

        await HumanBehaviorUtility.stochastic_sleep(SLEEP_SHORT_MS)
        logger.info(f"Extracted post URL: {post_url}")
        return post_url


class ExtractPostContentElement(BaseWorkflowElement):

    def __init__(self):
        super().__init__("ExtractPostContentElement")

    async def execute(self, page: Page, post_url: str) -> str:
        logger.info(f"Navigating to post URL to extract content: {post_url}")
        await self.clear_page_state(page)

        try:
            await page.goto(post_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
        except Exception:
            logger.warning("Navigation timeout reached during post load, continuing execution...", extra={"postUrl": post_url})

        await HumanBehaviorUtility.stochastic_sleep(PAGE_LOAD_WAIT_MS)
        await HumanBehaviorUtility.human_scroll_scan(page)

        post_content = await page.evaluate(
            """(selectors) => {
                const extractAllTextNodes = (node) => {
                    let text = "";
                    node.childNodes.forEach(child => {
                        if (child.nodeType === Node.TEXT_NODE) {
                            text += child.textContent;
                        } else if (child.nodeType === Node.ELEMENT_NODE) {
                            text += extractAllTextNodes(child);
                        }
                    });
                    return text;
                };

                const commentaryContainers = document.querySelectorAll(selectors.COMMENTARY_CONTAINER);
                const rawTextsArray = Array.from(commentaryContainers).map(container => extractAllTextNodes(container));
                return rawTextsArray.join('\\n');
            }""",
            SELECTORS,
        )

        logger.info(f"Post content extracted successfully. Length: {len(post_content)} chars")
        await HumanBehaviorUtility.reading_dwell_time(len(post_content))
        return post_content


class LikePostElement(BaseWorkflowElement):

    def __init__(self):
        super().__init__("LikePostElement")

    async def execute(self, page: Page) -> dict[str, str]:
        logger.info("Checking and executing like action on post with smooth scroll.")
        
        like_button_exists = await page.query_selector(SELECTORS["LIKE_BUTTON"])
        if like_button_exists:
            await HumanBehaviorUtility.smooth_scroll_to_element(page, SELECTORS["LIKE_BUTTON"])

        like_status = await page.evaluate(
            """async (selectors) => {
                const likeButton = document.querySelector(selectors.LIKE_BUTTON);
                if (!likeButton) {
                    return { action: 'skipped', reason: 'not_found' };
                }

                const isPressed = likeButton.getAttribute('aria-pressed');
                if (isPressed === 'true') {
                    return { action: 'skipped', reason: 'already_liked' };
                } else {
                    likeButton.click();
                    return { action: 'clicked', reason: 'success' };
                }
            }""",
            SELECTORS,
        )

        await HumanBehaviorUtility.stochastic_sleep(SLEEP_LIKE_MS)
        logger.info("Like workflow completed.", extra={"likeStatus": like_status})
        return like_status


class PublishCommentElement(BaseWorkflowElement):

    def __init__(self):
        super().__init__("PublishCommentElement")

    async def execute(self, page: Page, comment_text: str) -> None:
        logger.info("Inserting and publishing generated comment via human typing dynamics.")
        
        await HumanBehaviorUtility.human_type(page, SELECTORS["COMMENT_EDITOR_BOX"], comment_text)
        await HumanBehaviorUtility.stochastic_sleep(SLEEP_INSERT_MS)

        published = await page.evaluate(
            """async (selectors) => {
                const commentButton = document.querySelector('button.comments-comment-box__submit-button--cr, button.artdeco-button--primary') ||
                    Array.from(document.querySelectorAll('button')).find(el => {
                        const text = el.textContent ? el.textContent.trim() : '';
                        const ariaLabel = el.getAttribute('aria-label') || '';
                        return text === 'Comment' || text === 'Post' || ariaLabel.toLowerCase().includes('comment');
                    });

                if (!commentButton) return false;
                const clickableElement = commentButton.closest('button, div[role="button"], a') || commentButton;
                if (clickableElement.hasAttribute('disabled') || clickableElement.getAttribute('aria-disabled') === 'true') {
                    return false;
                }

                clickableElement.click();
                return true;
            }""",
            SELECTORS,
        )

        if not published:
            raise RuntimeError("Publish comment button not found or is disabled.")

        await HumanBehaviorUtility.stochastic_sleep(SLEEP_PUBLISH_MS)
        logger.info("Comment published successfully.")


class MultiProfileAutomationElement(BaseWorkflowElement):

    def __init__(self):
        super().__init__("MultiProfileAutomationElement")

    async def execute(self, page: Page) -> dict[str, str]:
        logger.info("Starting multi-profile automation execution.")

        async def log_from_browser(level: str, message: str):
            if level == "error":
                logger.error(message)
            elif level == "warn":
                logger.warning(message)
            else:
                logger.info(message)

        await page.expose_function("logFromBrowser", log_from_browser)

        profile_execution_stats = await page.evaluate(
            """async (args) => {
                const [sleepShort, sleepModal, sleepContext, sleepLike, selectors] = args;
                const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
                const logInfo = (msg) => window.logFromBrowser ? window.logFromBrowser('info', msg) : console.log(msg);
                const logWarn = (msg) => window.logFromBrowser ? window.logFromBrowser('warn', msg) : console.warn(msg);
                const logErr = (msg) => window.logFromBrowser ? window.logFromBrowser('error', msg) : console.error(msg);

                const detailedStates = [];
                logInfo("Starting multi-profile automation script...");

                const switcherBtn = document.querySelector(selectors.PROFILE_SWITCHER_BTN);
                if (!switcherBtn) {
                    logErr("Error: Profile switcher toggle button not found!");
                    return { totalProfiles: 0, profilesProcessed: [] };
                }

                switcherBtn.click();
                await sleep(sleepShort);

                const profileItems = document.querySelectorAll(selectors.MODAL_ITEMS);
                if (!profileItems || profileItems.length === 0) {
                    logErr("Error: No profile options found in the modal.");
                    switcherBtn.click();
                    return { totalProfiles: 0, profilesProcessed: [] };
                }

                const totalProfiles = profileItems.length;
                logInfo(`Found ${totalProfiles} total profiles. Closing initial modal to begin loop...`);
                
                switcherBtn.click();
                await sleep(sleepModal);

                for (let i = 0; i < totalProfiles; i++) {
                    logInfo(`========================================`);
                    logInfo(`Processing Profile Index [${i + 1} of ${totalProfiles}]`);
                    logInfo(`========================================`);

                    const profileStateRecord = {
                        index: i,
                        profileNameOrIndex: `Profile #${i + 1}`,
                        likeState: 'pending',
                        repostState: 'pending',
                        commentState: i === 0 ? 'delivered_primary' : 'delivered_via_switch'
                    };

                    const openBtn = document.querySelector(selectors.PROFILE_SWITCHER_BTN);
                    if (!openBtn) {
                        logErr("Error: Switcher button could not be found.");
                        profileStateRecord.error = "Switcher button not found";
                        detailedStates.push(profileStateRecord);
                        break;
                    }
                    openBtn.click();
                    await sleep(sleepShort);

                    const currentModalItems = document.querySelectorAll(selectors.MODAL_ITEMS);
                    const currentItem = currentModalItems[i];

                    if (!currentItem) {
                        logWarn(`Warning: Profile list item at index ${i} is missing. Skipping...`);
                        profileStateRecord.likeState = 'skipped_missing_item';
                        profileStateRecord.repostState = 'skipped_missing_item';
                        detailedStates.push(profileStateRecord);
                        continue;
                    }

                    const radioInput = currentItem.querySelector('input[type="radio"]');
                    const label = currentItem.querySelector('label');

                    if (label) {
                        label.click();
                        logInfo(`-> Clicked profile label for index ${i}`);
                    } else if (radioInput) {
                        radioInput.click();
                        logInfo(`-> Clicked profile radio input for index ${i}`);
                    } else {
                        logErr(`-> Error: Could not find clickable radio/label element for index ${i}`);
                        profileStateRecord.likeState = 'failed_selection';
                        profileStateRecord.repostState = 'failed_selection';
                        detailedStates.push(profileStateRecord);
                        openBtn.click();
                        continue;
                    }

                    await sleep(sleepModal);

                    const saveButton = document.querySelector(selectors.SAVE_BUTTON);
                    if (saveButton) {
                        saveButton.click();
                        logInfo("-> Clicked 'Save' profile button.");
                    } else {
                        logWarn("-> Warning: Separate save button not explicitly found.");
                    }

                    await sleep(sleepContext);

                    if (i === 0) {
                        logInfo("-> First profile (Index 0) processed: Skipping Like and Repost actions as requested.");
                        profileStateRecord.likeState = 'skipped_primary_account';
                        profileStateRecord.repostState = 'skipped_primary_account';
                        detailedStates.push(profileStateRecord);
                        continue;
                    }

                    const likeBtn = document.querySelector(selectors.LIKE_BUTTON);
                    if (likeBtn) {
                        const isAlreadyLiked = likeBtn.getAttribute('aria-pressed') === 'true';
                        if (!isAlreadyLiked) {
                            likeBtn.click();
                            logInfo("-> Verified: Like button was not active. Clicked 'Like'.");
                            profileStateRecord.likeState = 'delivered_clicked';
                            await sleep(sleepLike);
                        } else {
                            logInfo("-> Verified: Like button is already clicked/active for this profile. Skipping.");
                            profileStateRecord.likeState = 'already_liked';
                        }
                    } else {
                        logErr("-> Error: Like button element not found on page.");
                        profileStateRecord.likeState = 'failed_not_found';
                    }

                    const firstRepostBtn = document.querySelector(selectors.REPOST_BTN_FIRST);
                    if (firstRepostBtn) {
                        firstRepostBtn.click();
                        logInfo("-> Clicked first Repost button (opened dropdown).");
                        await sleep(sleepShort);

                        const secondRepostItem = document.querySelector(`${selectors.REPOST_ITEM_SECOND}`)?.closest('[role="button"]') ||
                                               document.querySelector('.social-reshare-button__sharing-as-is-dropdown-item');
                        
                        if (secondRepostItem) {
                            secondRepostItem.click();
                            logInfo("-> SUCCESS: Clicked the correct second Repost option (confirmed repost).");
                            profileStateRecord.repostState = 'delivered_reposted';
                            await sleep(sleepContext);
                        } else {
                            logErr("-> Error: Second repost dropdown item element not found.");
                            profileStateRecord.repostState = 'failed_second_item_not_found';
                        }
                    } else {
                        logErr("-> Error: First repost button not found.");
                        profileStateRecord.repostState = 'failed_first_button_not_found';
                    }

                    detailedStates.push(profileStateRecord);
                    logInfo(`Successfully completed workflow for profile index ${i}.`);
                }

                logInfo("========================================");
                logInfo("Automation sequence finished across all profiles!");
                logInfo("========================================");

                return { totalProfiles, profilesProcessed: detailedStates };
            }""",
            [SLEEP_SHORT_MS, SLEEP_MODAL_MS, SLEEP_CONTEXT_MS, SLEEP_LIKE_MS, SELECTORS],
        )

        logger.info("Multi-profile automation execution completed.", extra={"profileExecutionStats": profile_execution_stats})
        return profile_execution_stats