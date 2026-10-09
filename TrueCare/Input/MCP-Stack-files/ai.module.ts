import { Module } from '@nestjs/common';
import { PrismaModule } from '../prisma/prisma.module'; // TODO(prisma)
import { AuthModule } from '../auth/auth.module';       // TODO: your auth module
import { McpController } from './mcp/mcp.controller';
import { McpServerFactory } from './mcp/mcp-server.factory';
import { AiAuditService } from './audit/ai-audit.service';
import { SolverProvider } from './solver/solver.provider';
import { OrchestratorService } from './orchestrator/orchestrator.service';

@Module({
  imports: [PrismaModule, AuthModule],
  controllers: [McpController],
  providers: [McpServerFactory, AiAuditService, SolverProvider, OrchestratorService],
  exports: [OrchestratorService],
})
export class AiModule {}
