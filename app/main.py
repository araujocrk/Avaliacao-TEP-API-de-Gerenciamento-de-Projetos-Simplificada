from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title='API de Gerenciamento de Projetos Simplificada',
    description='API para um sistema interno de gerenciamento de mini-projetos',
    version='0.1.0'
)

# Classe usando Enum para limitar valores (bem integrado com Pydantic)
class PrioridadeEnum(int, Enum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3
    
# Classe usando Enum para limitar valores (bem integrado com Pydantic)
class StatusEnum(str, Enum):
    PLANEJADO = 'Planejado'
    EM_ANDAMENTO = 'Em Andamento'
    CONCLUIDO = 'Concluído'
    CANCELADO = 'Cancelado'

# Classe usando BaseModel para validação automática de dados, parsing e serialização
class ProjectCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    prioridade: PrioridadeEnum
    status: StatusEnum
    
class Project(ProjectCreate):
    project_id: int
    criado_em: datetime
    
# Simulação de um banco de dados (em memória)
projects_db = {}
    
counter_id = 1

# Rota post para criação dos projetos.
# Retorna a classe Project criada e status HTTP 201.
@app.post('/projects/create', response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    global counter_id
    project_id = counter_id
    new_project = Project(project_id=project_id, criado_em=datetime.utcnow(), **project.model_dump())
    projects_db[project_id] = new_project
    counter_id += 1
    return new_project
    