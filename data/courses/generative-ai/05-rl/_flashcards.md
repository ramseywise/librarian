---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/05-rl/slides/deck.yaml
cards:
- front: Name the sources of reward this lecture goes through, in order.
  back: The parts change the source of the reward, from humans to a constitution to a checker to an environment, while the question stays the same.
  lesson: generative-ai/05-rl/readme
- front: Name four things this lecture teaches you to do with a trained model.
  back: You will be able to say what a model was actually asked to do, where its score came from and how it could be gamed.
  lesson: generative-ai/05-rl/readme
- front: What are the steps of the agent-environment loop?
  back: An agent sees a state, acts, and receives a reward and a new state, and training adjusts its policy to raise total reward.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: What happened to the bandit agent at epsilon 0, 0.1 and 0.5?
  back: Some exploration is necessary but too much is wasteful, as 0.1 beat both 0 and 0.5 in this bandit.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: In a language model, what plays the roles of state, action and policy?
  back: The conversation is the state, the next token the action and the weights the policy, which leaves the reward as your design decision.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: How do dynamic programming, Monte Carlo and TD differ?
  back: TD learning updates from one step plus its own estimate, trading some bias for lower variance and online learning.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: What does the PPO clip do to the objective once the ratio passes 1 + epsilon?
  back: PPO clips the objective so a batch can be reused safely, but this removes an incentive rather than enforcing a hard bound.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Why do Q-learning and SARSA take different paths in the cliff world?
  back: Q-learning learns the greedy policy off-policy, while SARSA learns the exploring policy on-policy and so avoids the cliff.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: How fast does regret grow for explore-then-commit, UCB, MOSS and Exp3?
  back: With fixed gaps regret grows like log n, in the worst case like √n, and no policy beats √n on every instance.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: Why does LinUCB beat UCB when there are many arms?
  back: LinUCB's regret depends on the feature dimension rather than the number of arms, provided the linear model holds.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: Which bandit method fits drift, rankings, recommendations and sampling from a posterior?
  back: Match the algorithm to the goal first; a regret rate for one goal says little about another.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: What does Bayesian regret hide?
  back: Bayesian regret is an average over a prior and does not bound any single instance.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
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
- front: What does the DPO loss do when both answers become more likely?
  back: DPO optimizes the gap in log-ratios against a frozen reference, needing no reward model or sampling but unable to explore beyond its pairs.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: On math, how did offline DPO compare with semi-online DPO and GRPO in Lanchantin et al.?
  back: Going online matters more than the specific loss on reasoning, since online DPO and GRPO both beat offline DPO on math.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: Which methods need a reward model, a critic or paired data?
  back: Default to DPO with preference pairs and no verifier, and use GRPO when a checker can score new outputs online.
  lesson: generative-ai/05-rl/notes/03b-grpo-and-gspo
- front: Why does an all-correct or all-wrong group teach GRPO nothing?
  back: GRPO normalizes rewards within a group of samples, so it needs no critic but learns nothing from groups that all pass or all fail.
  lesson: generative-ai/05-rl/notes/03b-grpo-and-gspo
- front: Why does GSPO use a sequence-level ratio rather than GRPO's token ratio?
  back: GSPO matches the ratio to the unit that earns the reward, using one sequence-level ratio in place of per-token ratios.
  lesson: generative-ai/05-rl/notes/03b-grpo-and-gspo
- front: Which DPO variant answers which practical problem?
  back: DPO variants each change one thing, so choose by the problem you have, whether that's unpaired feedback, collapse, budget, length or missing labels.
  lesson: generative-ai/05-rl/notes/13-preference-variants
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
- front: Which post-training stage added the most for Phi-4-Mini-Reasoning?
  back: At 3.8B, bulk distillation has to come before a small curated SFT set or RL, and the stages together beat the 7B distilled baseline's 53.3.
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: Why can a simulated environment hurt, and how do you limit that?
  back: A distorted environment teaches strategies that die on deployment, so mix simulated rollouts with real ones and recalibrate regularly.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: How did quality and diversity affect LIMA's 7B fine-tune on 2,000 examples?
  back: Data quality and diversity both raise results, so start with about 50 good examples and fix the setup if they show no gain.
  lesson: generative-ai/05-rl/notes/06b-dataset-engineering-for-post-training
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
  lesson: generative-ai/05-rl/notes/07b-rl-for-tool-calling-and-dense-signals
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
- front: What makes RL different from supervised learning?
  back: There is no answer key. The agent acts, gets a reward that may be delayed, and has to work out which actions earned it.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: Define policy and value.
  back: A policy chooses actions in each situation. A value estimates the total future reward from an action or situation.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: Why explore at all?
  back: Without trying other options, the agent can lock onto whatever paid first and never learn that something better exists.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: What does the discount do?
  back: It weighs future reward against reward now; a lower discount makes the agent more short-sighted.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: How is a language model an RL agent?
  back: The conversation is the situation, the next word is the action, the weights are the policy. Add a reward and policy gradient training can adjust them.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: What is reward hacking?
  back: Scoring well on the reward while missing the goal it stood for, such as a chatbot that flatters for thumbs up.
  lesson: generative-ai/05-rl/notes/00-rl-in-plain-language
- front: Q-learning vs SARSA?
  back: Q-learning bootstraps from the best next action and learns the greedy policy (off-policy). SARSA bootstraps from the action actually taken and learns the exploring policy (on-policy).
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: What does a baseline do in REINFORCE?
  back: It subtracts expected return so that only better- or worse-than-expected actions move the policy. Variance falls, and the gradient stays unbiased.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: What is GAE?
  back: A λ-weighted sum of TD errors, trading bias (λ near 0) against variance (λ near 1).
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Why does PPO clip?
  back: To reuse a batch for several epochs without the policy moving too far from the one that collected it, and without TRPO's second-order machinery.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Is PPO on-policy?
  back: Data collection is on-policy and data is discarded soon after. The ratio corrects for drift within those few epochs.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: How does max-entropy RL differ?
  back: It adds policy entropy to the objective, so the agent keeps options open while it optimizes reward.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Which family do LLMs use and why?
  back: Policy methods. The action space is the whole vocabulary at each step, and no table or argmax over next actions is practical.
  lesson: generative-ai/05-rl/notes/01-rl-foundations
- front: Ordinary vs weighted importance sampling?
  back: Ordinary is unbiased with unbounded variance. Weighted is biased but the bias vanishes, and its variance is far lower, so it is preferred in practice.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: Why does TD beat Monte Carlo on a batch?
  back: TD(0) converges to the value of the maximum-likelihood Markov model of the data, so it uses structure (A leads to B). Monte Carlo fits the observed returns only.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: What does Expected SARSA change?
  back: It uses the expectation over next actions instead of a sample, which removes the variance of choosing `a'`. With a greedy target it is Q-learning.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: What is maximisation bias?
  back: The max over noisy estimates is biased upward. Double Q-learning selects with one table and evaluates with the other.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: What does planning buy in Dyna?
  back: No new information, but each real transition is propagated through the model, so credit spreads in far fewer episodes.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: Why n-step?
  back: Intermediate n trades the bias of one-step bootstrapping against the variance of the full return.
  lesson: generative-ai/05-rl/notes/01b-algorithm-families-td-and-dqn
- front: What is regret?
  back: The reward lost against always pulling the best arm, which equals the sum over arms of the gap times the expected pull count.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: Why is Thompson sampling attractive for large action sets?
  back: Linear Thompson sampling needs one linear programme per round, where LinUCB needs a maximisation over the confidence set; the regret rate matches in the Bayesian case.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: Bayesian or frequentist regret?
  back: Bayesian regret averages over a prior and does not bound any single instance; frequentist regret holds per instance.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: When is best-arm identification the right goal?
  back: When you recommend one arm after exploring, not when you pay for every pull; the two goals need different algorithms.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: What does UCRL2 add over UCB?
  back: Optimism over transition models of an MDP, re-planned only when a state-action count doubles; regret scales with the diameter.
  lesson: generative-ai/05-rl/notes/01c-bandit-algorithms
- front: Name the three stages.
  back: SFT on demonstrations, reward model on ranked pairs, PPO against the reward model with a KL penalty to the SFT model.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: How many models does PPO RLHF hold in memory?
  back: 'Four: policy, reference, reward model, value model.'
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: Why pairs instead of scores?
  back: Humans compare more consistently than they score. Bradley-Terry turns comparisons into a scalar.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: Why a KL penalty?
  back: It keeps the policy where the reward model can be trusted and limits reward hacking.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: What is the alignment tax?
  back: Capability benchmarks falling while alignment metrics improve. InstructGPT reduced it with PPO-ptx, by mixing pretraining-gradient updates into PPO.
  lesson: generative-ai/05-rl/notes/02-rlhf-pipeline
- front: What does DPO optimize?
  back: A logistic loss on the gap between the log-ratios of chosen and rejected against a frozen reference, with no reward model or sampling.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: What does β do in DPO?
  back: It sets how hard the reference pulls. Lower β moves further and tends to get wordier.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: When offline, when online?
  back: Offline for style and refusal with pairs available. Online for reasoning and tasks where a checker can score new behaviour.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: What is DPO's main failure?
  back: Length and format drift, plus no way to discover behaviour outside the dataset.
  lesson: generative-ai/05-rl/notes/03-preference-optimization
- front: Why did GRPO drop the critic?
  back: Advantage comes from comparison within a group of samples, saving roughly a policy-sized value model.
  lesson: generative-ai/05-rl/notes/03b-grpo-and-gspo
- front: Why GSPO?
  back: Token-level ratios fit poorly with whole-sequence rewards, so it uses a sequence-level ratio.
  lesson: generative-ai/05-rl/notes/03b-grpo-and-gspo
- front: What two phases does CAI have?
  back: SL-CAI (critique, revise, fine-tune on revisions) and RLAIF (AI preference labels, preference model, RL).
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: What does CAI replace?
  back: Human harmlessness labels. The optimizer stays the same, and helpfulness labels may still be human.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: Why is the constitution an advantage?
  back: Values become explicit, auditable and easy to change.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: What is the main risk of AI feedback?
  back: 'Correlated errors: noise averages out, shared bias does not.'
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: How is RLAIF different from RLHF at training time?
  back: Only the labeler. The reward model and PPO stages have the same shape.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: How does red-teaming relate?
  back: It supplies the hard prompts that the constitution's critique loop needs in order to be useful.
  lesson: generative-ai/05-rl/notes/04-constitutional-ai
- front: Why does SFT come before RL?
  back: RL scores the model's own outputs. If they don't parse as JSON or a valid tool call, the reward can't be computed, so SFT sets the form and RL then pursues the strategy ("form first, spirit second").
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: What does SFT teach, and what doesn't it?
  back: 'Protocol knowledge: format, style, process. It maximizes the likelihood of one reference, so it is a poor store of facts, which come from pretraining, continued pretraining or RAG.'
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: Why does RL generalize where SFT memorizes?
  back: RL optimizes reward on its own on-policy samples, so it re-solves under shift. In Chu et al., navigation with relative directions moved RL +11.0 pp and SFT −79.5 pp, at the same base model and compute.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: Can RL beat the model it was distilled from?
  back: Yes, because online training is capped by the task, not the data. Llama-Nemotron-Ultra reached 66.4 on GPQA-Diamond from SFT on R1 traces (teacher 71.5), and 76.0 after GRPO.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: Why does an LLM need so few trials next to Q-learning?
  back: Its prior makes the open-ended action space navigable. *Door* and *key* already mean something, so exploration is targeted, not blind.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: What are sensible LoRA defaults?
  back: All weight matrices, especially the MLPs, a learning rate about 10× full fine-tuning, rank 64–256 for SFT and 8–32 (even 1) for RL.
  lesson: generative-ai/05-rl/notes/05-post-training-for-agents
- front: When does SFT stop being enough?
  back: When more demonstrations stop improving held-out scenarios, or when format is stable but out-of-distribution performance is flat.
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: 'Correct process with a wrong answer, or wrong process with a right answer: which deserves more reward?'
  back: Outcome stays primary (RLVR), and verifiable process *violations* are penalized (RLVP). Don't reward "lucky" paths that broke a rule.
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: '$10k to improve a support agent: where does it go?'
  back: Mostly context, knowledge, prompts/Skills and programmatic constraints. Train weights only for what can't be stated (tone, perception) or for cost (distillation).
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: A per-customer LoRA instead of a knowledge base?
  back: It wins for stable style and implicit preferences. It loses for facts that change, need citations or must be deletable.
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: Long-tail rollouts idle the GPUs. What can you do?
  back: Run rollout and training asynchronously with a staleness cap and importance-ratio masking (10), cap or penalize length (DAPO's overlong shaping), use partial rollouts, and use dynamic batching.
  lesson: generative-ai/05-rl/notes/05b-choosing-sft-rl-or-no-training
- front: Why does the environment matter more than the algorithm?
  back: The policy learns whatever earns reward in the environment. A distorted environment produces strategies that die on deployment.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: Where can training data go wrong besides quality?
  back: Near-duplicates, eval contamination, unbalanced coverage, and synthetic data repeating the generator's errors.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: Where did instruction tuning come from?
  back: Two concurrent ICLR 2022 papers that rewrote NLP datasets as instructions and tested on task types held out of training.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: How many preference pairs do you need?
  back: 'It depends on the goal: see the table in this chapter, where task-level style or refusal changes need 100–10k.'
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: What is the handbook's shortcut for preference pairs?
  back: Use a real blog paragraph as chosen and an LLM answer as rejected, then filter.
  lesson: generative-ai/05-rl/notes/06-data-and-environments
- front: Why filter before you scale?
  back: In the LIMA ablation a 2,000-example set that was both high-quality and diverse beat sets that had only one of the two.
  lesson: generative-ai/05-rl/notes/06b-dataset-engineering-for-post-training
- front: Why is credit assignment harder for agents?
  back: Reward arrives at the end of a long trajectory, and the environment is only partly visible, so it's hard to tell which turn mattered.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: What does gate-then-rank do?
  back: A deterministic check zeroes wrong answers, and a judge orders only those that pass, so persuasion can't buy reward.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: What is RLVP?
  back: Outcome reward plus a per-action signal from a deterministic rule engine, normalized separately and combined.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: Why are environments asymmetric verifiers?
  back: '"Was this action bad?" is cheap to check. "Is this progress?" is about as hard as the task.'
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: Why not penalties alone?
  back: Inaction earns the best penalty score, so the agent stops trying.
  lesson: generative-ai/05-rl/notes/07-reward-design-and-tool-calling
- front: What does on-policy distillation add?
  back: Dense per-step signal from a stronger teacher on the states the student actually reaches.
  lesson: generative-ai/05-rl/notes/07b-rl-for-tool-calling-and-dense-signals
- front: What did DeepSeek-R1 show?
  back: Pure RL with verifiable rewards on a strong base model produced long chain-of-thought reasoning, without reasoning supervision.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: What is pass@k?
  back: The chance that at least one of k samples is correct. It measures what a model can reach, not what it usually does.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: What is the Yue et al. reading?
  back: RLVR sharpens paths the base model can already sample. At large k the base model can overtake it.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: Why does the distinction matter?
  back: It tells you whether to invest in RL, in search, or in the base model.
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: How little data can reasoning take?
  back: 'LIMA''s idea applied to long CoT: small SFT sets work on a strong base with a strong teacher, with s1 using 1,000 questions. Check the baseline before you believe the headline.'
  lesson: generative-ai/05-rl/notes/08-reasoning-rl-deepseek-r1
- front: What is best-of-N limited by?
  back: The selector. More samples help only if you can pick the good one.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: When does self-consistency work?
  back: When answers can be compared for equality and the correct answer is the most common.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: What does an aggregator like AggLM add?
  back: It can pick a minority answer or combine partial work, which a vote can't do.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: Why does refinement need training?
  back: Prompted models usually can't improve their own answers. SCoRe trains revision with multi-turn RL.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: What does AB-MCTS change in MCTS?
  back: 'It drops the fixed branching factor: each node can always sample a fresh answer, and Thompson sampling chooses wider or deeper.'
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: Search or training?
  back: Try search first when pass@k already covers the task and a verifier exists. Train when you need it fast at one sample.
  lesson: generative-ai/05-rl/notes/09-test-time-search-and-training
- front: How many seeds should you run?
  back: 'More than feels necessary: Colas et al. needed at least 15 to separate SAC from TD3 on one task. Plot per-seed curves, then test.'
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: What are the actors and learners for?
  back: Actors generate experience and learners update the policy, so sampling and optimization scale separately.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: How do you deploy a new RL policy?
  back: As an immutable release, with a canary or shadow stage. Stay as near to "never update live" as the problem allows.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: How do you make RL safe?
  back: Constrain the optimizer, filter actions, abort and reset, or add penalties, knowing penalties alone give no guarantee. It is an open problem.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: What's different about RL security?
  back: 'A bigger attack surface: rewards, observations and replay buffers can all be poisoned. Fix basics such as phishing and patching first.'
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: What has dated since 2020 in Winder's advice?
  back: Behaviour cloning is now the first step, critics are often dropped, and offline RL is partly solved for preferences.
  lesson: generative-ai/05-rl/notes/10-engineering-rl-systems
- front: Why is MARL non-stationary?
  back: Each agent is part of every other agent's environment, and all of them are learning at once.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: What is CTDE?
  back: 'Centralized training with decentralized execution: critics see everything during training, and actors use only local views in production.'
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: QMIX vs MADDPG?
  back: QMIX factorizes a joint value for cooperative discrete tasks. MADDPG gives each agent a critic over all actions, and it handles mixed cooperative-competitive settings.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: Why not independent learners?
  back: They are simple, but they can settle on safe poor outcomes. The matrix game above shows this.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: Where does RL fit in RAG?
  back: 'At decision points: query rewrite, evidence selection, continue-or-stop retrieval, tool use.'
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: RL or DPO for RAG?
  back: RL when you can score new behaviour online. DPO when you have preference pairs and want a cheap offline change.
  lesson: generative-ai/05-rl/notes/11-multi-agent-and-rag-rl
- front: Is it fixable with better data?
  back: Better data and bigger reward models shrink it. Casper et al. call it fundamental, because many rewards fit finite data and approval is not benefit.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: What did Stiennon et al. measure?
  back: Real preference rose up to about 10 nats of KL and fell after, while the reward model kept predicting wins. By KL 250 the two were anti-correlated.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: Why reverse KL?
  back: It penalizes mass where the reference has almost none, keeping the policy where the reward model can be trusted. It is also mode-seeking.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: Do verifiable rewards need a KL penalty?
  back: Many RLVR recipes drop it. It stays essential for learned rewards, and a partial verifier can still be exploited.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: What is WARM?
  back: Averaging the weights of reward models fine-tuned from one SFT checkpoint, which holds up longer at the inference cost of one model.
  lesson: generative-ai/05-rl/notes/12-rlhf-failure-modes
- front: When is KTO the right choice?
  back: Feedback is unpaired thumbs up or down. With clean transitive pairs, its authors say DPO will work better.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: What does IPO change?
  back: A squared loss toward a target margin, which stops pairs from collapsing toward zero probability on the rejected side.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: What does ORPO remove?
  back: The reference model and the second stage, by putting an odds-ratio term into the SFT loss.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: Where does SimPO's gain come from?
  back: Length normalization. Without it, its Mistral-7B-Base ablation scored below DPO.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: What did DiscoPOP teach?
  back: Searched losses gain little, validation reward accuracy didn't predict the benchmark, and the loss worked only near the β it was found at.
  lesson: generative-ai/05-rl/notes/13-preference-variants
- front: What does self-play need in place of preference labels?
  back: 'A definition of chosen: SFT data for SPIN, a user''s own text for DITTO, a win-rate model for SPPO, and rewrites from logged feedback for RLHI.'
  lesson: generative-ai/05-rl/notes/13-preference-variants
---
