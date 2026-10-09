import { Injectable } from '@nestjs/common';
import { createHash } from 'crypto';
import { PrismaService } from '../../prisma/prisma.service'; // TODO(prisma): your path
import { ToolContext } from '../scope/tool-context';

@Injectable()
export class AiAuditService {
  constructor(private readonly prisma: PrismaService) {}

  /** Wrap any tool handler so every call is timed, logged, and provider-tagged. */
  async wrap<T>(ctx: ToolContext, toolName: string, input: unknown, fn: () => Promise<T>): Promise<T> {
    const t0 = Date.now();
    try {
      const out = await fn();
      await this.write(ctx, toolName, input, t0, true, out);
      return out;
    } catch (e: any) {
      await this.write(ctx, toolName, input, t0, false, undefined, e?.message);
      throw e;
    }
  }

  private write(ctx: ToolContext, toolName: string, input: unknown, t0: number, ok: boolean, out?: unknown, error?: string) {
    return this.prisma.aiToolAudit.create({
      data: {
        providerId: ctx.providerId, userId: ctx.userId, channel: ctx.channel, toolName,
        input: input as any,
        outputHash: out ? createHash('sha256').update(JSON.stringify(out)).digest('hex') : null,
        durationMs: Date.now() - t0, ok, error,
      },
    });
  }
}
