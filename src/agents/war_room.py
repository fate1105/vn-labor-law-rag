"""
WAR ROOM ORCHESTRATOR — ĐIỀU PHỐI HỆ THỐNG AI ĐA TÁC NHÂN (MULTI-AGENT SYSTEM)
Mô hình phối hợp 5 Agent xử lý quy trình công việc pháp lý khép kín.
"""

import time
import json
import pathlib
from typing import Dict, Any, List, Optional, Callable, Generator
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from src.web.rag_service import RAGService, _call_gemini_with_retry, DEFAULT_LLM_MODEL
from src.agents.prompts import (
    AGENT_2_SOLUTION_PROMPT,
    AGENT_3_CRITIQUE_PROMPT,
    AGENT_4_DRAFTING_PROMPT,
    AGENT_5_EVALUATION_PROMPT,
)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


@dataclass
class AgentOutput:
    agent_id: str
    agent_name: str
    title: str
    content: str
    latency: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WarRoomResult:
    case_description: str
    total_latency: float
    agent1_retrieval: AgentOutput
    agent2_solutions: AgentOutput
    agent3_critique: AgentOutput
    agent4_draft: AgentOutput
    agent5_evaluation: AgentOutput

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_description": self.case_description,
            "total_latency": round(self.total_latency, 2),
            "agents": {
                "agent1_retrieval": {
                    "name": self.agent1_retrieval.agent_name,
                    "content": self.agent1_retrieval.content,
                    "latency": round(self.agent1_retrieval.latency, 2),
                    "metadata": self.agent1_retrieval.metadata,
                },
                "agent2_solutions": {
                    "name": self.agent2_solutions.agent_name,
                    "content": self.agent2_solutions.content,
                    "latency": round(self.agent2_solutions.latency, 2),
                },
                "agent3_critique": {
                    "name": self.agent3_critique.agent_name,
                    "content": self.agent3_critique.content,
                    "latency": round(self.agent3_critique.latency, 2),
                },
                "agent4_draft": {
                    "name": self.agent4_draft.agent_name,
                    "content": self.agent4_draft.content,
                    "latency": round(self.agent4_draft.latency, 2),
                },
                "agent5_evaluation": {
                    "name": self.agent5_evaluation.agent_name,
                    "content": self.agent5_evaluation.content,
                    "latency": round(self.agent5_evaluation.latency, 2),
                },
            },
        }


class WarRoomOrchestrator:
    """Bộ điều phối trung tâm vận hành phòng tác chiến 5 tác nhân (War Room)."""

    def __init__(self, rag_service: Optional[RAGService] = None, model_name: str = DEFAULT_LLM_MODEL):
        self.rag_service = rag_service or RAGService.get_instance()
        self.model_name = model_name
        self.client = self.rag_service.gemini_client

    def _call_agent_llm(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.25,
        max_output_tokens: int = 4096,
    ) -> str:
        """Thực thi gọi LLM chuyên biệt cho từng tác nhân."""
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        try:
            response = _call_gemini_with_retry(
                client=self.client,
                model=self.model_name,
                contents=user_message,
                config=config,
            )
            return response.text or "(Không có phản hồi từ Agent)"
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                return "⚠️ Tác nhân tạm thời đạt giới hạn số lượt gọi API miễn phí của tài khoản. Vui lòng thử lại sau vài giây hoặc cập nhật API key mới."
            return f"⚠️ Tác nhân gặp lỗi kết nối: {err_str}"

    def execute_stream(
        self,
        case_description: str,
        delay_between_agents: float = 1.0,
    ) -> Generator[Dict[str, Any], None, WarRoomResult]:
        """
        Thực thi tiến trình War Room theo dạng Generator:
        Yield kết quả của từng Agent ngay khi hoàn thành để hiển thị theo thời gian thực (Real-time).
        """
        t_start = time.time()

        # ── BƯỚC 1: AGENT 1 - RÀ SOÁT PHÁP LÝ (LEGAL RETRIEVER) ────────────────
        t0 = time.time()
        yield {"step": 1, "status": "running", "agent": "Agent 1 – Rà soát Pháp lý", "msg": "Đang tra cứu cơ sở dữ liệu pháp luật và kiểm tra hiệu lực văn bản..."}
        
        # Gọi mô-đun Effect-Aware RAG đã hoàn thiện từ trước
        retrieval_res = self.rag_service.run_effect_aware(
            query=case_description,
            top_k_retrieve=8,
            top_k_llm=6,
            model_name=self.model_name,
        )
        agent1_content = retrieval_res.get("answer", "")
        agent1_chunks = retrieval_res.get("chunks", [])
        agent1_stats = retrieval_res.get("effect_stats", {})
        agent1_latency = time.time() - t0

        agent1_out = AgentOutput(
            agent_id="agent_1",
            agent_name="Agent 1 – Rà soát Pháp lý (Legal Retriever)",
            title="Căn cứ Pháp lý & Tình trạng Hiệu lực Văn bản",
            content=agent1_content,
            latency=agent1_latency,
            metadata={
                "chunks": agent1_chunks,
                "effect_stats": agent1_stats,
            },
        )
        yield {"step": 1, "status": "completed", "agent": agent1_out.agent_name, "output": agent1_out}
        time.sleep(delay_between_agents)

        # ── BƯỚC 2: AGENT 2 - PHÂN TÍCH & ĐỀ XUẤT (SOLUTION AGENT) ─────────────
        t0 = time.time()
        yield {"step": 2, "status": "running", "agent": "Agent 2 – Phân tích & Đề xuất", "msg": "Đang khoanh vùng hành vi và xây dựng các phương án giải quyết..."}
        
        agent2_user_msg = f"""TÌNH HUỐNG / VỤ VIỆC:
{case_description}

CĂN CỨ PHÁP LÝ ĐÃ ĐƯỢC AGENT 1 RÀ SOÁT:
{agent1_content}

Dựa trên thông tin trên, hãy phân tích bản chất vụ việc và đề xuất các phương án giải quyết chi tiết."""

        agent2_content = self._call_agent_llm(
            system_prompt=AGENT_2_SOLUTION_PROMPT,
            user_message=agent2_user_msg,
        )
        agent2_latency = time.time() - t0

        agent2_out = AgentOutput(
            agent_id="agent_2",
            agent_name="Agent 2 – Phân tích & Đề xuất Giải pháp (Solution Agent)",
            title="Phân tích Bản chất & Đề xuất Phương án Xử lý",
            content=agent2_content,
            latency=agent2_latency,
        )
        yield {"step": 2, "status": "completed", "agent": agent2_out.agent_name, "output": agent2_out}
        time.sleep(delay_between_agents)

        # ── BƯỚC 3: AGENT 3 - PHẢN BIỆN (CRITIQUE AGENT) ────────────────────────
        t0 = time.time()
        yield {"step": 3, "status": "running", "agent": "Agent 3 – Phản biện Rủi ro", "msg": "Đang kiểm tra chéo, tìm lỗ hổng pháp lý và rủi ro tố tụng..."}

        agent3_user_msg = f"""TÌNH HUỐNG / VỤ VIỆC:
{case_description}

CÁC PHƯƠNG ÁN DO AGENT 2 ĐỀ XUẤT:
{agent2_content}

CĂN CỨ PHÁP LÝ LIÊN QUAN (AGENT 1):
{agent1_content}

Hãy đóng vai trò luật sư phản biện độc lập, chỉ rõ mọi rủi ro về thời hiệu, quy trình, nguy cơ khiếu kiện ngược và đưa ra biện pháp khắc phục cho từng phương án."""

        agent3_content = self._call_agent_llm(
            system_prompt=AGENT_3_CRITIQUE_PROMPT,
            user_message=agent3_user_msg,
        )
        agent3_latency = time.time() - t0

        agent3_out = AgentOutput(
            agent_id="agent_3",
            agent_name="Agent 3 – Phản biện & Đánh giá Rủi ro (Critique Agent)",
            title="Báo cáo Phản biện Rủi ro & Biện pháp Khắc phục",
            content=agent3_content,
            latency=agent3_latency,
        )
        yield {"step": 3, "status": "completed", "agent": agent3_out.agent_name, "output": agent3_out}
        time.sleep(delay_between_agents)

        # ── BƯỚC 4: AGENT 4 - SOẠN THẢO VĂN BẢN (DRAFTING AGENT) ───────────────
        t0 = time.time()
        yield {"step": 4, "status": "running", "agent": "Agent 4 – Soạn thảo Văn bản", "msg": "Đang lập dự thảo văn bản công vụ theo chuẩn Nghị định 30/2020/NĐ-CP..."}

        agent4_user_msg = f"""TÌNH HUỐNG / VỤ VIỆC:
{case_description}

CĂN CỨ PHÁP LÝ (AGENT 1):
{agent1_content}

PHƯƠNG ÁN XỬ LÝ (AGENT 2):
{agent2_content}

CÁC LƯU Ý PHÁP LÝ & RỦI RO (AGENT 3):
{agent3_content}

Hãy soạn thảo văn bản hành chính công vụ hoàn chỉnh theo đúng thể thức Nghị định số 30/2020/NĐ-CP để cán bộ sử dụng."""

        agent4_content = self._call_agent_llm(
            system_prompt=AGENT_4_DRAFTING_PROMPT,
            user_message=agent4_user_msg,
        )
        agent4_latency = time.time() - t0

        agent4_out = AgentOutput(
            agent_id="agent_4",
            agent_name="Agent 4 – Soạn thảo Văn bản Hành chính (Drafting Agent)",
            title="Dự thảo Văn bản Hành chính (Chuẩn NĐ 30/2020/NĐ-CP)",
            content=agent4_content,
            latency=agent4_latency,
        )
        yield {"step": 4, "status": "completed", "agent": agent4_out.agent_name, "output": agent4_out}
        time.sleep(delay_between_agents)

        # ── BƯỚC 5: AGENT 5 - TỔNG HỢP & ĐÁNH GIÁ (EVALUATION AGENT) ───────────
        t0 = time.time()
        yield {"step": 5, "status": "running", "agent": "Agent 5 – Tổng hợp & Đánh giá", "msg": "Đang lập ma trận so sánh đa tiêu chí và đưa ra khuyến nghị tối ưu..."}

        agent5_user_msg = f"""TỔNG HỢP TIẾN TRÌNH WAR ROOM:
1. TÌNH HUỐNG: {case_description}
2. CĂN CỨ PHÁP LÝ (AGENT 1):
{agent1_content}

3. PHƯƠNG ÁN ĐỀ XUẤT (AGENT 2):
{agent2_content}

4. PHẢN BIỆN RỦI RO (AGENT 3):
{agent3_content}

5. VĂN BẢN ĐÃ SOẠN THẢO (AGENT 4):
{agent4_content}

Hãy lập Báo cáo Tham mưu Tối ưu (Executive Summary) kèm Bảng ma trận so sánh chấm điểm các phương án và lộ trình hành động cụ thể cho Cán bộ."""

        agent5_content = self._call_agent_llm(
            system_prompt=AGENT_5_EVALUATION_PROMPT,
            user_message=agent5_user_msg,
        )
        agent5_latency = time.time() - t0

        agent5_out = AgentOutput(
            agent_id="agent_5",
            agent_name="Agent 5 – Tổng hợp & Đánh giá Quyết định (Evaluation Agent)",
            title="Báo cáo Tham mưu & Ma trận Ra Quyết định Tối ưu",
            content=agent5_content,
            latency=agent5_latency,
        )
        yield {"step": 5, "status": "completed", "agent": agent5_out.agent_name, "output": agent5_out}

        total_latency = time.time() - t_start
        final_result = WarRoomResult(
            case_description=case_description,
            total_latency=total_latency,
            agent1_retrieval=agent1_out,
            agent2_solutions=agent2_out,
            agent3_critique=agent3_out,
            agent4_draft=agent4_out,
            agent5_evaluation=agent5_out,
        )
        yield {"step": "all", "status": "finished", "result": final_result}
        return final_result

    def execute(self, case_description: str) -> WarRoomResult:
        """Thực thi toàn bộ tiến trình War Room và trả về kết quả cuối cùng."""
        gen = self.execute_stream(case_description, delay_between_agents=1.0)
        final_res = None
        for event in gen:
            if event.get("status") == "finished":
                final_res = event.get("result")
        return final_res

