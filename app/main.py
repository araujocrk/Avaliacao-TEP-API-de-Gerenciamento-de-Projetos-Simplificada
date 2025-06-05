from fastapi import FastAPI, HTTPException, Query, Path, Body, status
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
    id: int
    criado_em: str
    
# Simulação de um banco de dados (em memória)
projects_db = {}
    
# Variável global para incrementar o ID
counter_id = 1

# Rota POST para criação dos projetos.
# Retorna a classe Project criada e status HTTP 201.
@app.post('/projects/create', response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    
    global counter_id
    project_id = counter_id
    criado_em = datetime.utcnow()
    criado_em_formatado = criado_em.strftime('%d-%m-%Y %H:%M:%S')
    new_project = Project(id=project_id, criado_em=criado_em_formatado, **project.model_dump())
    projects_db[project_id] = new_project
    counter_id += 1
    return new_project
    
# Rota GET que lista os projetos com um limite (paginação)
@app.get('/projects', response_model=List[Project], status_code=status.HTTP_200_OK)
def list_projects(
    status: Optional[StatusEnum] = Query(None, description='Filtrar por status.'),
    prioridade: Optional[PrioridadeEnum] = Query(None, description='Filtrar por prioridade.'),
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, gt=0)
):
    
    projects = list(projects_db.values())
    
    if status:
        projects = [p for p in projects if p.status == status]
    if prioridade:
        projects = [p for p in projects if p.prioridade == prioridade]    
    return projects[skip: skip + limit]

# Rota GET que busca um projeto pelo ID
@app.get('/projects/{project_id}', response_model=Project, status_code=status.HTTP_200_OK)
def get_project(project_id: int = Path(..., ge=1, description='ID do projeto vindo como path parameter')):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f'Projeto com ID {project_id} não encontrado.')
    return project

# Rota PUT que atualiza um projeto pelo ID
@app.put('/projects/{project_id}', response_model=Project, status_code=status.HTTP_200_OK)
def update_project(
    project_id: int = Path(..., ge=1, description='ID do projeto vindo como path parameter'), 
    project: ProjectCreate = Body(..., description='Cria um ProjectCreate vindo do body.')
):
    
    stored_project = projects_db.get(project_id)
    if not stored_project:
        raise HTTPException(status_code=404, detail=f'Projeto com ID = {project_id} não encontrado.')
    updated_project = Project(id=project_id, criado_em=stored_project.criado_em, **project.model_dump())
    projects_db[project_id] = updated_project
    return updated_project

@app.delete('/projects/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int = Path(..., ge=1, description='ID do projeto vindo como path parameter')):
    
    if project_id in projects_db:
        del projects_db[project_id]
        # return {'message': f'Projeto com ID {project_id} deletado com sucesso.'}
    else:
        raise HTTPException(status_code=404, detail=f'Projeto com ID {project_id} não encontrado.')