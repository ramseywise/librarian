---
imported_hash: f9f494042205f124
decks:
- learn-ai-engineering/generative-ai/05-RL/slides/deck.yaml
cards:
- front: What are the steps of the agent-environment loop?
  back: An agent sees a state, acts, and receives a reward and a new state, and training adjusts its policy to raise total reward.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: What happened to the bandit agent at epsilon 0, 0.1 and 0.5?
  back: Some exploration is necessary but too much is wasteful, as 0.1 beat both 0 and 0.5 in this bandit.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: How do dynamic programming, Monte Carlo and TD differ?
  back: TD learning updates from one step plus its own estimate, trading some bias for lower variance and online learning.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Why do Q-learning and SARSA take different paths in the cliff world?
  back: Q-learning learns the greedy policy off-policy, while SARSA learns the exploring policy on-policy and so avoids the cliff.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: What does the PPO clip do to the objective once the ratio passes 1 + epsilon?
  back: PPO clips the objective so a batch can be reused safely, but this removes an incentive rather than enforcing a hard bound.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: In a language model, what plays the roles of state, action and policy?
  back: The conversation is the state, the next token the action and the weights the policy, which leaves the reward as your design decision.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: What are the three stages of RLHF and why does SFT come first?
  back: RLHF runs SFT on demonstrations, trains a reward model on ranked pairs, then applies PPO with a KL penalty to the SFT model.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: In Ovadia et al., which scored higher on current-events QA, RAG or fine-tuning?
  back: On a current-events QA set, retrieval reached 0.875 and fine-tuning at most 0.588, so try prompts and retrieval before fine-tuning.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: How does the Bradley-Terry model turn pairwise preferences into a scalar reward?
  back: A reward model learns a scalar so that score differences predict which answer people prefer, and it inherits their disagreement.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: What does overoptimization look like on the Stiennon et al. chart?
  back: A reward model is a proxy, so optimizing past its region of validity raises predicted quality while true quality falls.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: What are the common forms of reward hacking, and what mitigates them?
  back: Verbosity, sycophancy and mode collapse are common reward hacks, and a tuned KL penalty is the first defence.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: Which methods need a reward model, a critic or paired data?
  back: Default to DPO with preference pairs and no verifier, and use GRPO when a checker can score new outputs online.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: Which DPO variant answers which practical problem?
  back: DPO variants each change one thing, so choose by the problem you have, whether that's unpaired feedback, collapse, budget, length or missing labels.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: What does the DPO loss do when both answers become more likely?
  back: DPO optimizes the gap in log-ratios against a frozen reference, needing no reward model or sampling but unable to explore beyond its pairs.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: Why does an all-correct or all-wrong group teach GRPO nothing?
  back: GRPO normalizes rewards within a group of samples, so it needs no critic but learns nothing from groups that all pass or all fail.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: Why does GSPO use a sequence-level ratio rather than GRPO's token ratio?
  back: GSPO matches the ratio to the unit that earns the reward, using one sequence-level ratio in place of per-token ratios.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: On math, how did offline DPO compare with semi-online DPO and GRPO in Lanchantin et al.?
  back: Going online matters more than the specific loss on reasoning, since online DPO and GRPO both beat offline DPO on math.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: What two phases does Constitutional AI have?
  back: CAI critiques and revises answers for SFT in its first phase, then trains RL on AI preference labels in its second.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: Why does more data not fix a length-biased labeler?
  back: More labels wash out random noise but never shared bias, so a consistent AI labeler still needs a human-labeled audit set.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: What limits self-improvement loops according to the chapter?
  back: AI feedback can match human labels, but loops work best with a checkable answer, and untrained self-correction often makes answers worse.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: Why does SFT come before RL in post-training?
  back: SFT establishes a parseable form first, since RL scores the model's own outputs and learns noise if they can't be parsed.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: What did Chu et al. find when rules or cities shifted between train and test?
  back: Under distribution shift RL re-solves the task and holds up, while SFT applies old answers and degrades, by 79.5 points in one test.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: How does a prior that is right 70% of the time change exploration on an 11-move puzzle?
  back: A language model starts with useful priors, so its exploration is targeted, whereas a tabular agent must discover everything by chance.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: How did quality and diversity affect LIMA's 7B fine-tune on 2,000 examples?
  back: Data quality and diversity both raise results, so start with about 50 good examples and fix the setup if they show no gain.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: Why can a simulated environment hurt, and how do you limit that?
  back: A distorted environment teaches strategies that die on deployment, so mix simulated rollouts with real ones and recalibrate regularly.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: Which reward forms say where a failed call went wrong?
  back: A scalar reward says only how good a call was, while vector or generative rewards point to which phase went wrong.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: Why does the gate-then-rank reward give a persuasive wrong answer zero?
  back: Gate a learned judge behind a deterministic check, so wrong answers earn zero however persuasive they are.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: Why do verifiable process penalties restore GRPO's gradient on all-fail groups?
  back: Environments can cheaply verify that an action was bad, so penalties restore within-group variance even when every rollout fails.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: Why must environment tokens be masked out of the RL loss?
  back: Mask tool output from the loss, expect RL to cost far more than SFT, and consider denser signals like distillation when one scalar is too sparse.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: What did Yue et al. find about what RLVR adds at large k?
  back: RLVR raises pass@1 by concentrating on paths the base already has, and at large k the base can solve more problems.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: Why can pass@1 mislead about whether RL created a skill?
  back: The pass@k curve shows whether RL added reach or only sharpened it, which pass@1 alone can't tell you.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: What limits best-of-N, and how did vote and checker compare with perfect selection?
  back: More samples help only if you can pick the good one, so a flawed checker falls well short of pass@k at the same N.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: How does rStar-Math turn search into training data?
  back: Search trajectories are rollouts, so a verified search can generate the training data that makes the next search stronger.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: How large a gap appears between identical agents with 3, 5 and 15 seeds?
  back: Identical agents show a typical 14-point gap at three seeds, so a small win on few seeds usually proves nothing.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: How should you roll out a new RL policy and why stay near never updating live?
  back: Treat each policy update as an immutable release with canary or shadow stages, and learn live only when the problem requires it.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: Which 2020 views about RL no longer hold for LLMs?
  back: LLM RL reversed classic advice because a pretrained model changes the problem, making behaviour cloning the first step and critics optional.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: What does centralized training with decentralized execution mean?
  back: CTDE tackles non-stationarity by giving critics global information during training while each actor acts on local observations at deployment.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: What actions and rewards does RL use at each RAG decision point?
  back: Apply RL in RAG where decisions chain and reward arrives late, and tie that reward to the answer rather than to retrieval metrics.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: What are the rules of thumb for RL and alignment?
  back: Every method here is only as good as its reward, so ask what the score is and how the model could game it.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: Which pillars and lab come after RL and alignment?
  back: Run the lab to see reward at work, then take these signals into observability and applications.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
---
