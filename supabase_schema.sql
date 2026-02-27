-- Supabase schema for Voint backend
-- Static tables: read-only from backend
-- Dynamic tables: written by the pipeline and sandbox

------------------------------------------------------------
-- Static table: cards
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cards (
    id                  uuid PRIMARY KEY,
    name                text NOT NULL,
    issuer              text NOT NULL,
    network             text NOT NULL,  -- visa | mastercard | amex | rupay | diners

    -- Cost
    annual_fee_inr      numeric NOT NULL,
    forex_fee_pct       numeric DEFAULT 0,      -- e.g. 3.5 for 3.5%
    fuel_surcharge_waiver boolean DEFAULT false,
    fuel_surcharge_cap_inr numeric NULL,

    -- Reward earning
    welcome_bonus_pts   integer NOT NULL,
    welcome_spend_inr   numeric NOT NULL,
    welcome_months      integer NOT NULL,

    -- Eligibility
    credit_score_min    integer NOT NULL,
    approval_prob       numeric NOT NULL,      -- 0–1

    -- Reward value
    point_value_inr     numeric NOT NULL,      -- ₹ per base point/mile
    monthly_total_cap_inr numeric NULL,
    reward_expiry_months integer NULL,

    -- Status
    is_active           boolean NOT NULL DEFAULT true
);


------------------------------------------------------------
-- Static table: reward_rates
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reward_rates (
    id                  uuid PRIMARY KEY,
    card_id             uuid NOT NULL REFERENCES cards(id),
    category            text NOT NULL,         -- groceries | dining | travel | fuel | online | entertainment | utilities | other
    points_per_100      numeric NOT NULL,      -- points earned per ₹100
    monthly_cap_inr     numeric NULL,
    reward_type         text NOT NULL,         -- points | miles | cashback
    rate_variance_pct   numeric NULL,         -- used in simulation
    accelerator_note    text NULL
);


------------------------------------------------------------
-- Static table: transfer_partners
-- (useful for Agent 2 transfer uplift)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transfer_partners (
    id                  uuid PRIMARY KEY,
    card_id             uuid NOT NULL REFERENCES cards(id),
    partner_program     text NOT NULL,
    partner_type        text NOT NULL,        -- airline | hotel | wallet | other
    transfer_ratio      numeric NOT NULL,     -- e.g. 2.0 means 2 card pts -> 1 partner pt
    min_transfer_pts    integer NOT NULL,
    transfer_fee_inr    numeric NOT NULL DEFAULT 0,
    cpp_inr             numeric NOT NULL      -- cents-per-point equivalent in ₹
);


------------------------------------------------------------
-- Dynamic table: sessions
-- (created in POST /api/analyze, status updated by pipeline)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id                  uuid PRIMARY KEY,
    goal_text           text NOT NULL,
    goal_amount_inr     numeric NOT NULL,
    timeline_months     integer NOT NULL,
    monthly_spend_inr   numeric NOT NULL,
    cards_owned         uuid[] NOT NULL,
    risk_level          text NOT NULL,        -- low | medium | high
    credit_score_range  text NOT NULL,
    spend_breakdown     jsonb NOT NULL,       -- {"groceries": 8000, ...}
    status              text NOT NULL,        -- pending | processing | complete | failed
    created_at          timestamptz NOT NULL DEFAULT now()
);


------------------------------------------------------------
-- Dynamic table: strategy_results
-- (written by pipeline after Agents 2 & 3, updated by Agent 5)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_results (
    id                  uuid PRIMARY KEY,
    session_id          uuid NOT NULL UNIQUE REFERENCES sessions(id),

    monthly_plan        jsonb NOT NULL,       -- list[MonthPlan]
    recommended_cards   jsonb NOT NULL,       -- list[RecommendedCard]

    total_rewards_inr   numeric NOT NULL,
    total_fees_inr      numeric NOT NULL,
    net_value_inr       numeric NOT NULL,

    -- From Agent 3 (yield)
    yield_index         numeric NULL,
    break_even_month    integer NULL,

    -- From Agent 5 (LLM narrative)
    ai_narrative        text NULL,

    created_at          timestamptz NOT NULL DEFAULT now()
);


------------------------------------------------------------
-- Dynamic table: simulation_results
-- (written once per session by Agent 4)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulation_results (
    id                  uuid PRIMARY KEY,
    session_id          uuid NOT NULL UNIQUE REFERENCES sessions(id),

    success_probability numeric NOT NULL,
    p10_inr             numeric NOT NULL,
    p50_inr             numeric NOT NULL,
    p90_inr             numeric NOT NULL,
    worst_case_inr      numeric NOT NULL,
    best_case_inr       numeric NOT NULL,
    risk_score          numeric NOT NULL,
    histogram_data      jsonb NOT NULL,       -- [{"bucket_inr": 15000, "count": 423}, ...]
    run_count           integer NOT NULL,

    created_at          timestamptz NOT NULL DEFAULT now()
);


------------------------------------------------------------
-- Dynamic table: sandbox_runs
-- (written by Agent 6 for sandbox mode)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sandbox_runs (
    id                  uuid PRIMARY KEY,
    session_id          uuid NOT NULL REFERENCES sessions(id),

    selected_cards      uuid[] NOT NULL,
    spend_overrides     jsonb NOT NULL,       -- {card_id: {category: amount}}

    computed_rewards_inr numeric NOT NULL,
    yield_index         numeric NOT NULL,
    diff_vs_ai_inr      numeric NOT NULL,

    simulation_result   jsonb NULL,

    created_at          timestamptz NOT NULL DEFAULT now()
);

