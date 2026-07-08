# ============================================================
# GigHub API – Complete main.py
# Admission Number: C027-01-0873/2024
# ============================================================

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import Optional

# ==================== FastAPI App ====================
app = FastAPI(
    title="GigHub API – C027-01-0873/2024",
    description="API to manage freelance gig listings in Nairobi",
    version="1.0.0"
)

# ==================== In-Memory Database ====================
# 8 gigs (5 + last digit 3) – categories: Marketing, Data, Consulting – currency: KES
gigs_db = [
    {
        "id": 1,
        "title": "Social Media Marketing for Fashion Brand",
        "description": "Manage social media accounts for a new Nairobi-based fashion brand. Create content, schedule posts, and engage with followers to grow brand awareness.",
        "category": "Marketing",
        "budget": 25000.0,
        "currency": "KES",
        "status": "Open",
        "client_name": "Wanjiru Mwangi"
    },
    {
        "id": 2,
        "title": "Data Analysis for Retail Sales",
        "description": "Analyze sales data from a local retail chain and provide insights on customer behavior and product performance. Deliver a dashboard with key metrics.",
        "category": "Data",
        "budget": 35000.0,
        "currency": "KES",
        "status": "In Progress",
        "client_name": "James Ochieng"
    },
    {
        "id": 3,
        "title": "Business Strategy Consulting for Startup",
        "description": "Help a fintech startup refine their go-to-market strategy. Conduct market research, competitor analysis, and provide a strategic roadmap.",
        "category": "Consulting",
        "budget": 45000.0,
        "currency": "KES",
        "status": "Open",
        "client_name": "Amina Hassan"
    },
    {
        "id": 4,
        "title": "Digital Marketing Campaign for E-commerce",
        "description": "Plan and execute a 3-month digital marketing campaign for an e-commerce platform. Focus on Google Ads and Instagram to increase sales by 20%.",
        "category": "Marketing",
        "budget": 30000.0,
        "currency": "KES",
        "status": "Closed",
        "client_name": "Brian Kiprop"
    },
    {
        "id": 5,
        "title": "Data Entry & Cleaning for NGO",
        "description": "Clean and organize a large dataset of survey responses for a local NGO. Ensure data accuracy and prepare it for analysis.",
        "category": "Data",
        "budget": 15000.0,
        "currency": "KES",
        "status": "Open",
        "client_name": "Faith Akinyi"
    },
    {
        "id": 6,
        "title": "HR Consulting for SME",
        "description": "Advise a growing SME on setting up HR policies, recruitment processes, and employee performance management systems.",
        "category": "Consulting",
        "budget": 40000.0,
        "currency": "KES",
        "status": "In Progress",
        "client_name": "David Odhiambo"
    },
    {
        "id": 7,
        "title": "Content Marketing for Tech Blog",
        "description": "Write and distribute blog posts and articles for a tech blog targeting Kenyan developers. Improve SEO and increase organic traffic.",
        "category": "Marketing",
        "budget": 20000.0,
        "currency": "KES",
        "status": "Open",
        "client_name": "Grace Muthoni"
    },
    {
        "id": 8,
        "title": "Market Research for New Product",
        "description": "Conduct market research to identify consumer needs and pricing strategies for a new beverage product launching in Nairobi.",
        "category": "Consulting",
        "budget": 38000.0,
        "currency": "KES",
        "status": "Open",
        "client_name": "Peter Njoroge"
    }
]

# ==================== Pydantic Models ====================

class GigCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100, description="Title of the gig")
    description: str = Field(..., min_length=20, max_length=500, description="Detailed description")
    category: str = Field(..., description="Must be one of: Marketing, Data, Consulting")
    budget: float = Field(..., gt=0, description="Budget must be greater than 0")
    client_name: str = Field(..., min_length=2, max_length=50, description="Client's full name")

    @validator('category')
    def category_must_be_valid(cls, v):
        allowed_categories = ["Marketing", "Data", "Consulting"]
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of {allowed_categories}')
        return v


class GigUpdate(BaseModel):
    budget: Optional[float] = Field(None, gt=0, description="New budget (optional)")
    status: Optional[str] = Field(None, description="New status (optional): Open, In Progress, or Closed")

    @validator('status')
    def status_must_be_valid(cls, v):
        if v is not None and v not in ["Open", "In Progress", "Closed"]:
            raise ValueError('Status must be "Open", "In Progress", or "Closed"')
        return v


# ==================== API Endpoints ====================

@app.get("/gigs")
def list_gigs(
    category: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None
):
    """List all gigs, with optional filtering by category and budget range."""
    result = gigs_db
    if category:
        result = [g for g in result if g["category"].lower() == category.lower()]
    if min_budget is not None:
        result = [g for g in result if g["budget"] >= min_budget]
    if max_budget is not None:
        result = [g for g in result if g["budget"] <= max_budget]
    return result


@app.get("/gigs/{gig_id}")
def get_gig(gig_id: int):
    """Return a single gig by ID. Returns 404 if not found."""
    for gig in gigs_db:
        if gig["id"] == gig_id:
            return gig
    raise HTTPException(status_code=404, detail="Gig not found")


@app.get("/gigs/search")
def search_gigs(q: str):
    """Search for gigs by title (case-insensitive partial match)."""
    q_lower = q.lower()
    results = [g for g in gigs_db if q_lower in g["title"].lower()]
    return results


@app.post("/gigs")
def create_gig(gig: GigCreate):
    """Create a new gig. Auto-generates ID, sets currency=KES, status=Open."""
    new_id = max([g["id"] for g in gigs_db]) + 1 if gigs_db else 1
    new_gig = {
        "id": new_id,
        "title": gig.title,
        "description": gig.description,
        "category": gig.category,
        "budget": gig.budget,
        "currency": "KES",
        "status": "Open",
        "client_name": gig.client_name
    }
    gigs_db.append(new_gig)
    return {"message": "Gig created successfully", "gig": new_gig}


@app.put("/gigs/{gig_id}")
def update_gig(gig_id: int, update: GigUpdate):
    """Update budget and/or status of an existing gig. Returns 404 if not found."""
    for idx, gig in enumerate(gigs_db):
        if gig["id"] == gig_id:
            if update.budget is not None:
                gigs_db[idx]["budget"] = update.budget
            if update.status is not None:
                gigs_db[idx]["status"] = update.status
            return {"message": "Gig updated successfully", "gig": gigs_db[idx]}
    raise HTTPException(status_code=404, detail="Gig not found")


@app.delete("/gigs/{gig_id}")
def delete_gig(gig_id: int):
    """Delete a gig by ID. Returns 404 if not found."""
    for idx, gig in enumerate(gigs_db):
        if gig["id"] == gig_id:
            deleted = gigs_db.pop(idx)
            return {"message": "Gig deleted successfully", "gig": deleted}
    raise HTTPException(status_code=404, detail="Gig not found")